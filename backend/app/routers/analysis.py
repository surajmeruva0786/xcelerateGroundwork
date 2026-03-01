from datetime import datetime
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import IndustrialArea, SatelliteRun
from app.services.analysis import run_full_analysis_for_industrial_area
from app.services.reports import generate_satellite_run_report_pdf


class RunAnalysisRequest(BaseModel):
    industrial_area_id: str = Field(
        ..., description="UUID of the industrial area to analyse"
    )
    t1_date: datetime = Field(..., description="Start date for pre-period (T1)")
    t2_date: datetime = Field(..., description="Start date for post-period (T2)")


class PlotResultSummary(BaseModel):
    plot_id: str
    plot_number: str
    risk_level: str
    risk_score: float
    has_encroachment: bool
    is_vacant: bool
    is_partial_construction: bool
    is_closed: bool


class RunAnalysisResponse(BaseModel):
    satellite_run_id: str
    industrial_area_id: str
    t1_date: datetime
    t2_date: datetime
    status: str
    plots: List[PlotResultSummary]


router = APIRouter()


@router.post("/run-analysis", response_model=RunAnalysisResponse)
def run_analysis(
    payload: RunAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Trigger a full geospatial compliance analysis for a given industrial area.

    This endpoint:
    - Creates a SatelliteRun record
    - Fetches Sentinel-2 multi-temporal imagery
    - Applies SCL-based cloud masking
    - Computes NDVI and NDBI
    - Detects built-up and vegetation
    - Finds encroachments and road misalignments
    - Computes per-plot metrics and assigns risk scores
    """
    industrial_area = (
        db.query(IndustrialArea)
        .filter(IndustrialArea.id == payload.industrial_area_id)
        .first()
    )
    if not industrial_area:
        raise HTTPException(status_code=404, detail="Industrial area not found")

    satellite_run = SatelliteRun(
        id=uuid4(),
        industrial_area_id=industrial_area.id,
        run_type="ad_hoc_triggered",
        t1_date=payload.t1_date,
        t2_date=payload.t2_date,
        status="running",
    )
    db.add(satellite_run)
    db.commit()
    db.refresh(satellite_run)

    try:
        plot_results = run_full_analysis_for_industrial_area(
            db=db,
            industrial_area=industrial_area,
            satellite_run=satellite_run,
        )
        satellite_run.status = "completed"
        satellite_run.finished_at = datetime.utcnow()
        db.commit()
    except Exception as exc:  # pragma: no cover - defensive logging
        satellite_run.status = "failed"
        satellite_run.error_message = str(exc)
        satellite_run.finished_at = datetime.utcnow()
        db.commit()
        raise

    summaries: List[PlotResultSummary] = []
    for result, plot in plot_results:
        summaries.append(
            PlotResultSummary(
                plot_id=str(plot.id),
                plot_number=plot.plot_number,
                risk_level=result.risk_level,
                risk_score=result.risk_score,
                has_encroachment=result.has_encroachment,
                is_vacant=result.is_vacant,
                is_partial_construction=result.is_partial_construction,
                is_closed=result.is_closed,
            )
        )

    return RunAnalysisResponse(
        satellite_run_id=str(satellite_run.id),
        industrial_area_id=str(industrial_area.id),
        t1_date=satellite_run.t1_date,
        t2_date=satellite_run.t2_date,
        status=satellite_run.status,
        plots=summaries,
    )


@router.get("/{satellite_run_id}/report.pdf")
def download_report(
    satellite_run_id: str,
    db: Session = Depends(get_db),
):
    """Download a PDF compliance report for a given satellite run."""
    satellite_run = (
        db.query(SatelliteRun).filter(SatelliteRun.id == satellite_run_id).first()
    )
    if not satellite_run:
        raise HTTPException(status_code=404, detail="Satellite run not found")

    pdf_bytes = generate_satellite_run_report_pdf(db=db, satellite_run=satellite_run)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="run_{satellite_run_id}.pdf"'
        },
    )



