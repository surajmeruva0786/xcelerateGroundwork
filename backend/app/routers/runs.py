from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import SatelliteRun


class RunSummary(BaseModel):
  id: str
  industrial_area_id: str
  t1_date: str
  t2_date: str
  status: str


router = APIRouter()


@router.get("/runs", response_model=List[RunSummary])
def list_runs(db: Session = Depends(get_db)):
  runs = db.query(SatelliteRun).order_by(SatelliteRun.created_at.desc()).limit(20).all()
  return [
    RunSummary(
      id=str(r.id),
      industrial_area_id=str(r.industrial_area_id),
      t1_date=r.t1_date.isoformat(),
      t2_date=r.t2_date.isoformat(),
      status=r.status,
    )
    for r in runs
  ]


