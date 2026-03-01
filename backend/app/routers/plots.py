from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.models.models import Plot, PlotAnalysisResult


class PlotSummary(BaseModel):
    id: str
    industrial_area_id: str
    plot_number: str
    approved_land_use: str | None


class PlotLatestAnalysis(BaseModel):
    plot: PlotSummary
    last_result_id: str | None
    risk_level: str | None
    risk_score: float | None
    has_encroachment: bool | None
    is_vacant: bool | None
    is_partial_construction: bool | None
    is_closed: bool | None


router = APIRouter()


@router.get("/", response_model=list[PlotSummary])
def list_plots(db: Session = Depends(get_db)) -> List[PlotSummary]:
    plots = db.query(Plot).all()
    return [
        PlotSummary(
            id=str(p.id),
            industrial_area_id=str(p.industrial_area_id),
            plot_number=p.plot_number,
            approved_land_use=p.approved_land_use,
        )
        for p in plots
    ]


@router.get("/latest-analysis", response_model=list[PlotLatestAnalysis])
def list_plots_with_latest_analysis(
    db: Session = Depends(get_db),
) -> List[PlotLatestAnalysis]:
    plots = db.query(Plot).all()
    responses: list[PlotLatestAnalysis] = []
    for plot in plots:
        last_result = (
            db.query(PlotAnalysisResult)
            .filter(PlotAnalysisResult.plot_id == plot.id)
            .order_by(PlotAnalysisResult.created_at.desc())
            .first()
        )
        responses.append(
            PlotLatestAnalysis(
                plot=PlotSummary(
                    id=str(plot.id),
                    industrial_area_id=str(plot.industrial_area_id),
                    plot_number=plot.plot_number,
                    approved_land_use=plot.approved_land_use,
                ),
                last_result_id=str(last_result.id) if last_result else None,
                risk_level=last_result.risk_level if last_result else None,
                risk_score=last_result.risk_score if last_result else None,
                has_encroachment=last_result.has_encroachment if last_result else None,
                is_vacant=last_result.is_vacant if last_result else None,
                is_partial_construction=last_result.is_partial_construction
                if last_result
                else None,
                is_closed=last_result.is_closed if last_result else None,
            )
        )
    return responses


@router.get("/geojson")
def plots_geojson(db: Session = Depends(get_db)):
    """Return all plots as a GeoJSON FeatureCollection for map visualisation."""
    # Use ST_AsGeoJSON to serialise PostGIS geometries efficiently.
    sql = text(
        """
        SELECT
          id::text,
          industrial_area_id::text,
          plot_number,
          ST_AsGeoJSON(approved_layout_geom) AS geom
        FROM plots
        """
    )
    rows = db.execute(sql).mappings().all()

    features = []
    for row in rows:
        features.append(
            {
                "type": "Feature",
                "id": row["id"],
                "geometry": row["geom"],
                "properties": {
                    "plot_number": row["plot_number"],
                    "industrial_area_id": row["industrial_area_id"],
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}



