import json
import logging
import os
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from backend.agent.actions import execute_action
from backend.database import models

logger = logging.getLogger(__name__)
print(f"[DEBUG] GEMINI_API_KEY loaded: {os.getenv('GEMINI_API_KEY')}")  # ADD THIS

async def process_alert(alert: models.Alert, db: Session):
    logger.info(f"Processing alert {alert.id}: {alert.alert_type} at {alert.station_id}")

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")

        context = {
            "alert_id": alert.id,
            "station_id": alert.station_id,
            "fuel_type": alert.fuel_type,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"""You are an autonomous fuel station monitoring agent.
Choose exactly one action: reorder, notify_manager, or escalate.
Respond ONLY with valid JSON: {{"action": "...", "reason": "..."}}
No extra text outside the JSON.

Alert Context:
{json.dumps(context, indent=2)}

Choose ONE action:
1. "reorder" — stock is critically low
2. "notify_manager" — price anomaly or high consumption  
3. "escalate" — critical situation needing human intervention

Respond with ONLY JSON: {{"action": "...", "reason": "..."}}"""}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 256,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code != 200:
                logger.error(f"Gemini error body: {response.text}")
            response.raise_for_status()

        response_data = response.json()
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        logger.info(f"LLM response: {response_text}")

        try:
            parsed = json.loads(response_text)
            action = parsed.get("action", "escalate")
            reason = parsed.get("reason", "No reason provided")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse response: {response_text}")
            action = "escalate"
            reason = "Failed to parse LLM response"

        await execute_action(action, alert, db, reason)

        alert.status = "acknowledged"
        alert.handled_by = "agent"
        alert.handled_at = datetime.utcnow()
        db.commit()

        logger.info(f"Alert {alert.id} processed with action: {action}")

    except Exception as e:
        logger.error(f"Error in responder: {e}")
        if "403" not in str(e) and "401" not in str(e):
            alert.status = "acknowledged"
            alert.handled_by = "system"
            alert.handled_at = datetime.utcnow()
            db.commit()
