from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import IndustrialArea, SatelliteRun
from app.services.analysis import run_full_analysis_for_industrial_area


def _run_monthly_analysis_job():
    """Scheduler job: run analysis for all industrial areas once a month.

    This is designed to be lightweight and idempotent. In production, you may
    want a more robust job runner (Celery, separate worker service).
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        # Use previous month as T1 and current month as T2 for change detection.
        t2_date = datetime(now.year, now.month, 1)
        prev_month = t2_date - timedelta(days=30)
        t1_date = datetime(prev_month.year, prev_month.month, 1)

        areas = db.query(IndustrialArea).all()
        for area in areas:
            satellite_run = SatelliteRun(
                industrial_area_id=area.id,
                run_type="scheduled_monthly",
                t1_date=t1_date,
                t2_date=t2_date,
                status="running",
            )
            db.add(satellite_run)
            db.commit()
            db.refresh(satellite_run)

            try:
                run_full_analysis_for_industrial_area(
                    db=db, industrial_area=area, satellite_run=satellite_run
                )
                satellite_run.status = "completed"
            except Exception as exc:  # pragma: no cover
                satellite_run.status = "failed"
                satellite_run.error_message = str(exc)
            finally:
                satellite_run.finished_at = datetime.utcnow()
                db.commit()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Start APScheduler in background for monthly analysis."""
    scheduler = BackgroundScheduler(timezone="UTC")
    # Cron expression from settings is for reference; we schedule here directly monthly.
    scheduler.add_job(
        _run_monthly_analysis_job,
        trigger="cron",
        day=1,
        hour=3,
        minute=0,
        id="monthly_industrial_analysis",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


