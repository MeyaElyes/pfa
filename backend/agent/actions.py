"""
Step 6 — Actions
reorder(), notify_manager(), escalate() functions
Can just log to DB/file for now
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import models
import os   
import json 
import asyncio
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


async def execute_action(action: str, alert: models.Alert, db: Session, reason: str = ""):
    """
    Execute the specified action on an alert.
    The db session is passed for future integration with persistence (e.g., ActionLog table).
    Currently, all actions just log to stdout/logger.
    """
    logger.info(f"Executing action '{action}' for alert {alert.id}: {reason}")
    
    if action == "reorder":
        await reorder(alert, db, reason)
    elif action == "notify_manager":
        await notify_manager(alert, db, reason)
    elif action == "escalate":
        await escalate(alert, db, reason)
    else:
        logger.warning(f"Unknown action: {action}")

    # persist an incident log for auditability
    try:
        incident = models.IncidentLog(
            alert_id=alert.id,
            action=action,
            reason=reason,
            payload=json.dumps({
                "station_id": alert.station_id,
                "fuel_type": alert.fuel_type,
                "message": alert.message,
                "severity": alert.severity,
            }),
            actor="agent"
        )
        db.add(incident)
        db.commit()
        logger.info(f"Incident logged id={incident.id} for alert {alert.id}")
    except Exception as e:
        logger.exception(f"Failed to write incident log: {e}")


async def reorder(alert: models.Alert, db: Session, reason: str):
    """
    Reorder fuel for the station.
    For now, just log the action.
    TODO: Integrate with supplier/inventory system
    """
    log_entry = f"[REORDER] Station {alert.station_id} ({alert.fuel_type}): {reason}"
    logger.info(log_entry)
    
    # Could save to a separate ActionLog table if needed
    # For now just log it


async def notify_manager(alert: models.Alert, db: Session, reason: str):
    """
    Notify the manager about an anomaly.
    For now, just log the action.
    TODO: Send email/SMS/Slack notification
    """
    log_entry = f"[NOTIFY_MANAGER] Station {alert.station_id} ({alert.fuel_type}): {reason}"
    logger.info(log_entry)
    
    # Try to send email if SMTP configuration is present
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "0")) if os.getenv("SMTP_PORT") else None
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    email_from = os.getenv("SMTP_FROM") or smtp_user
    email_to = os.getenv("MANAGER_EMAIL")

    if smtp_host and smtp_port and smtp_user and smtp_pass and email_to:
        subject = f"[Alert] {alert.station_id} {alert.fuel_type} - {alert.alert_type}"
        body = f"Station: {alert.station_id}\nFuel: {alert.fuel_type}\nSeverity: {alert.severity}\n\nMessage:\n{alert.message}\n\nReason:\n{reason}\n\nTimestamp: {alert.timestamp}\n"

        try:
            await _send_email_async(email_from, email_to, subject, body, smtp_host, smtp_port, smtp_user, smtp_pass, smtp_use_tls)
            logger.info(f"Email notification sent to {email_to}")
        except Exception as e:
            logger.exception(f"Failed to send notification email: {e}")
    else:
        logger.info("SMTP not fully configured; skipping email send")


async def escalate(alert: models.Alert, db: Session, reason: str):
    """
    Escalate to a human operator.
    For now, just log the action.
    TODO: Send alert to operator dashboard
    """
    log_entry = f"[ESCALATE] Station {alert.station_id} ({alert.fuel_type}): {reason}"
    logger.info(log_entry)
    
    # Could send to a Slack channel or dashboard here
    # For now just log it


async def _send_email_async(frm: str, to: str, subject: str, body: str, host: str, port: int, user: str, password: str, use_tls: bool = True):
    """Send email in a thread to avoid blocking the event loop."""
    def _send():
        msg = EmailMessage()
        msg['From'] = frm
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)

        if use_tls:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls()
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                server.login(user, password)
                server.send_message(msg)

    await asyncio.to_thread(_send)
