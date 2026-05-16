import asyncio
import logging

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database import models
from backend.agent.responder import process_alert

# Configure logging so messages actually show in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def watch_critical_alerts():
    print("🔍 Alert Watcher started")  # use print as backup
    logger.info("🔍 Alert Watcher started")

    while True:
        db: Session = SessionLocal()
        try:
            critical_alerts = db.query(models.Alert).filter(
                models.Alert.status == "new",
                models.Alert.severity == "critical"
            ).all()

            print(f"[WATCHER] Polled — found {len(critical_alerts)} critical new alert(s)")

            for alert in critical_alerts:
                try:
                    print(f"[WATCHER] Handing off alert {alert.id} ({alert.alert_type}) to responder...")
                    await process_alert(alert, db)
                except Exception as e:
                    print(f"[WATCHER] Error processing alert {alert.id}: {e}")

        except Exception as e:
            print(f"[WATCHER] Error: {e}")
        finally:
            db.close()

        await asyncio.sleep(30)


def start_watcher():
    asyncio.create_task(watch_critical_alerts())