from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Boolean,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class IndustrialArea(Base):
    __tablename__ = "industrial_areas"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    boundary = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    plots = relationship("Plot", back_populates="industrial_area")
    satellite_runs = relationship("SatelliteRun", back_populates="industrial_area")


class Plot(Base):
    __tablename__ = "plots"

    id = Column(UUID(as_uuid=True), primary_key=True)
    industrial_area_id = Column(
        UUID(as_uuid=True), ForeignKey("industrial_areas.id"), nullable=False
    )
    plot_number = Column(String, nullable=False)
    approved_land_use = Column(String, nullable=True)
    approved_layout_geom = Column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )
    approved_road_centerlines = Column(
        Geometry(geometry_type="MULTILINESTRING", srid=4326), nullable=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    plot_metadata = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    industrial_area = relationship("IndustrialArea", back_populates="plots")
    analysis_results = relationship(
        "PlotAnalysisResult", back_populates="plot", cascade="all, delete-orphan"
    )
    encroachments = relationship(
        "EncroachmentPolygon", back_populates="plot", cascade="all, delete-orphan"
    )


class SatelliteRun(Base):
    __tablename__ = "satellite_runs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    industrial_area_id = Column(
        UUID(as_uuid=True), ForeignKey("industrial_areas.id"), nullable=False
    )

    run_type = Column(
        String, nullable=False
    )  # e.g. "scheduled_monthly" or "ad_hoc_triggered"
    t1_date = Column(DateTime, nullable=False)
    t2_date = Column(DateTime, nullable=False)

    sentinel_collection = Column(String, default="COPERNICUS/S2_SR_HARMONIZED")
    cloud_coverage_threshold = Column(Float, default=40.0)  # percentage

    status = Column(
        String, default="pending"
    )  # pending, running, completed, failed, partially_completed
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    industrial_area = relationship("IndustrialArea", back_populates="satellite_runs")
    plot_results = relationship(
        "PlotAnalysisResult", back_populates="satellite_run", cascade="all, delete-orphan"
    )


class PlotAnalysisResult(Base):
    __tablename__ = "plot_analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True)
    plot_id = Column(UUID(as_uuid=True), ForeignKey("plots.id"), nullable=False)
    satellite_run_id = Column(
        UUID(as_uuid=True), ForeignKey("satellite_runs.id"), nullable=False
    )

    # Per-plot metrics (in square meters where applicable)
    built_up_area_m2 = Column(Float, nullable=False)
    plot_area_m2 = Column(Float, nullable=False)
    vacant_area_m2 = Column(Float, nullable=False)
    encroached_area_m2 = Column(Float, default=0.0, nullable=False)
    road_alignment_deviation_m = Column(Float, nullable=True)

    built_up_percentage = Column(Float, nullable=False)
    vacant_percentage = Column(Float, nullable=False)

    # High-level classification
    is_vacant = Column(Boolean, default=False, nullable=False)
    is_partial_construction = Column(Boolean, default=False, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)
    has_encroachment = Column(Boolean, default=False, nullable=False)

    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    recommended_action = Column(String, nullable=False)

    # NDVI / NDBI statistics to aid manual review
    mean_ndvi = Column(Float, nullable=True)
    mean_ndbi = Column(Float, nullable=True)

    raw_stats = Column(
        JSON, nullable=True
    )  # store detailed per-pixel statistics if needed

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plot = relationship("Plot", back_populates="analysis_results")
    satellite_run = relationship("SatelliteRun", back_populates="plot_results")


class EncroachmentPolygon(Base):
    __tablename__ = "encroachment_polygons"

    id = Column(UUID(as_uuid=True), primary_key=True)
    plot_id = Column(UUID(as_uuid=True), ForeignKey("plots.id"), nullable=False)
    satellite_run_id = Column(
        UUID(as_uuid=True), ForeignKey("satellite_runs.id"), nullable=False
    )

    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    encroached_area_m2 = Column(Float, nullable=False)
    encroachment_type = Column(
        String, nullable=False
    )  # e.g. "builtup_outside_boundary", "road_overlap"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plot = relationship("Plot", back_populates="encroachments")


