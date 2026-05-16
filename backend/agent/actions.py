"""
Step 6 — Actions
reorder(), notify_manager(), escalate() functions
Can just log to DB/file for now
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import models

logger = logging.getLogger(__name__)


async def execute_action(action: str, alert: models.Alert, db: Session, reason: str = ""):
    """
    Execute the specified action.
    For now, all actions just log to the database.
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
    
    # Could integrate with email/Slack here
    # For now just log it


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
