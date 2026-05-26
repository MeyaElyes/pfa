"""
services/retriever.py
---------------------
RAG retriever for historical alert context.

On startup the index is populated with all existing alerts from the backend.
Each chat turn uses semantic search to find the most relevant past incidents
and injects them into the LLM system prompt as grounding context — enabling
the agent to answer pattern and history questions that live tool calls cannot.
"""

from __future__ import annotations
import hashlib
import logging

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "alerts_rag"


def _alert_to_doc(alert: dict) -> str:
    return (
        f"[{alert.get('severity', '').upper()}] "
        f"{alert.get('alert_type', '')} at station {alert.get('station_id', '')} "
        f"for {alert.get('fuel_type', '')}: {alert.get('message', '')}"
    )


class AlertRetriever:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=DefaultEmbeddingFunction(),
        )

    def index_alerts(self, alerts: list[dict]) -> int:
        """Upsert alerts into the vector index. Returns number of docs indexed."""
        if not alerts:
            return 0
        docs, ids, metas = [], [], []
        for alert in alerts:
            doc = _alert_to_doc(alert)
            uid = str(alert.get("id") or hashlib.md5(doc.encode()).hexdigest())
            docs.append(doc)
            ids.append(uid)
            metas.append({
                "station_id": str(alert.get("station_id", "")),
                "alert_type": str(alert.get("alert_type", "")),
                "severity":   str(alert.get("severity", "")),
                "timestamp":  str(alert.get("timestamp", "")),
            })
        self._collection.upsert(documents=docs, ids=ids, metadatas=metas)
        logger.info("RAG: upserted %d alerts (index total=%d)", len(docs), self.count())
        return len(docs)

    def retrieve(self, query: str, station_id: str | None = None, k: int = 5) -> str:
        """
        Return a formatted context string of the k most relevant past alerts.
        Falls back to unfiltered search if station-specific query fails.
        Returns empty string if the index is empty or retrieval fails.
        """
        total = self.count()
        if total == 0:
            return ""
        n = min(k, total)
        where = {"station_id": station_id} if station_id else None
        try:
            results = self._collection.query(query_texts=[query], n_results=n, where=where)
        except Exception:
            if not where:
                return ""
            # Station filter may fail if no docs exist for that station yet
            try:
                results = self._collection.query(query_texts=[query], n_results=n)
            except Exception as exc:
                logger.warning("RAG retrieval failed: %s", exc)
                return ""

        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return ""

        lines = ["Relevant historical alert context (past incidents):"]
        for doc, meta in zip(docs, metas):
            ts = str(meta.get("timestamp", ""))[:16]
            lines.append(f"  - [{ts}] {doc}")
        return "\n".join(lines)

    def count(self) -> int:
        return self._collection.count()


# Module-level singleton shared by gemini_service and main
alert_retriever = AlertRetriever()
