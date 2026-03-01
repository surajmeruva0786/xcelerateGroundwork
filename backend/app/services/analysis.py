"""
High-level geospatial analysis pipeline for industrial plot compliance.

This module performs:
- Multi-temporal Sentinel-2 compositing (T1 vs T2)
- NDVI / NDBI-based built-up & vegetation detection
- Vectorisation of built-up mask
- Overlay with approved plot boundaries
- Encroachment & vacancy detection
- Road alignment discrepancy computation
- Risk scoring for each plot
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from datetime import datetime

import ee
from geoalchemy2.shape import to_shape
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union
from sqlalchemy.orm import Session

from app.models.models import (
    IndustrialArea,
    Plot,
    SatelliteRun,
    PlotAnalysisResult,
    EncroachmentPolygon,
)
from app.services.gee_client import (
    build_s2_composite_with_indices,
    derive_builtup_and_vegetation_masks,
    initialize_gee,
)


@dataclass
class RiskConfig:
    encroachment_high_threshold_pct: float = 5.0
    partial_construction_builtup_min_pct: float = 5.0
    partial_construction_builtup_max_pct: float = 40.0
    vacant_builtup_max_pct: float = 5.0


RISK_CONFIG = RiskConfig()


def _plot_geom_to_ee(plot: Plot) -> ee.Geometry:
    """Convert SQLAlchemy PostGIS geometry to Earth Engine geometry."""
    geom = to_shape(plot.approved_layout_geom)
    return ee.Geometry(mapping(geom))


def _area_m2(geom) -> float:
    """Compute area in square metres using planar approximation (UTM recommended upstream).

    For government deployments this should be replaced by area in an appropriate
    projected CRS (e.g. UTM zone for Chhattisgarh). Here we assume the geometry
    is already stored in EPSG:4326 and use shapely's area after local projection
    is applied at ETL time.
    """
    return float(geom.area)


def _compute_risk_flags_and_score(
    builtup_pct: float,
    vacant_pct: float,
    encroachment_pct: float,
) -> Tuple[bool, bool, bool, str, float, str]:
    """Apply rule-based risk logic described in requirements.

    Returns:
        is_vacant, is_partial, is_closed, risk_level, risk_score, recommended_action
    """
    is_vacant = builtup_pct <= RISK_CONFIG.vacant_builtup_max_pct
    is_partial = (
        RISK_CONFIG.partial_construction_builtup_min_pct
        < builtup_pct
        <= RISK_CONFIG.partial_construction_builtup_max_pct
    )
    # For this prototype, "closed" is approximated as very low built-up but high vacancy.
    is_closed = is_vacant and vacant_pct > 50.0

    risk_level = "LOW"
    risk_score = 0.0
    recommended_action = "Compliant; routine monitoring."

    if encroachment_pct > RISK_CONFIG.encroachment_high_threshold_pct or (
        is_closed and vacant_pct > 50.0
    ):
        risk_level = "HIGH"
        risk_score = 0.9
        recommended_action = (
            "High-priority site inspection; initiate legal notice for encroachment/closure."
        )
    elif is_partial:
        risk_level = "MEDIUM"
        risk_score = 0.6
        recommended_action = (
            "Issue show-cause notice; enforce construction and utilisation timelines."
        )

    return is_vacant, is_partial, is_closed, risk_level, risk_score, recommended_action


def _detect_road_alignment_deviation(
    approved_roads_geom,
    builtup_polygons: List[Polygon],
) -> float | None:
    """Compute spatial deviation between approved road centerlines and actual road edges.

    In this simplified implementation we:
    - Assume that roads remain largely non-built-up linear gaps between built-up clusters
    - Derive an approximate road mask by buffering built-up and inverting (free space)
    - Sample shortest distance from approved road lines to nearest free-space area edge

    A more advanced production implementation would use dedicated road extraction
    (e.g. Canny edge detection on high-res imagery or ML-based road segmentation).
    """
    if not approved_roads_geom:
        return None

    approved = to_shape(approved_roads_geom)
    if isinstance(approved, LineString):
        approved_lines = [approved]
    elif isinstance(approved, MultiLineString):
        approved_lines = list(approved.geoms)
    else:
        return None

    if not builtup_polygons:
        return None

    builtup_union = unary_union(builtup_polygons)
    # Approximate road corridors as gaps between built-up buffers
    buffer_dist = 5.0  # metres; tune based on typical road width
    builtup_buffer = builtup_union.buffer(buffer_dist)

    # In practice we would intersect with industrial area extent;
    # here we just measure distance to built-up edge as an indicator.
    deviations: list[float] = []
    for line in approved_lines:
        deviation = line.distance(builtup_buffer)
        deviations.append(float(deviation))

    if not deviations:
        return None
    # Mean deviation in metres
    return sum(deviations) / len(deviations)


def run_full_analysis_for_industrial_area(
    db: Session,
    industrial_area: IndustrialArea,
    satellite_run: SatelliteRun,
) -> List[Tuple[PlotAnalysisResult, Plot]]:
    """Execute end-to-end multi-temporal analysis for all plots in an industrial area."""
    initialize_gee()

    area_geom = to_shape(industrial_area.boundary)
    ee_aoi = ee.Geometry(mapping(area_geom))

    # Build T1 and T2 composites with NDVI/NDBI
    composite_t1 = build_s2_composite_with_indices(
        ee_aoi, satellite_run.t1_date, satellite_run.t1_date
    )
    composite_t2 = build_s2_composite_with_indices(
        ee_aoi, satellite_run.t2_date, satellite_run.t2_date
    )

    builtup_t2_mask, vegetation_t2_mask = derive_builtup_and_vegetation_masks(composite_t2)

    results: List[Tuple[PlotAnalysisResult, Plot]] = []

    plots: List[Plot] = (
        db.query(Plot).filter(Plot.industrial_area_id == industrial_area.id).all()
    )

    for plot in plots:
        ee_plot_geom = _plot_geom_to_ee(plot)

        # Pixel area statistics at plot level
        stats_t2 = builtup_t2_mask.addBands(vegetation_t2_mask).reduceRegion(
            reducer=ee.Reducer.sum().combine(
                reducer2=ee.Reducer.count(),
                sharedInputs=True,
            ),
            geometry=ee_plot_geom,
            scale=10,
            maxPixels=1_000_000,
        )

        stats_t2_info = stats_t2.getInfo()

        builtup_pixel_sum = float(stats_t2_info.get("BUILTUP_sum", 0.0))
        vegetation_pixel_sum = float(stats_t2_info.get("VEGETATION_sum", 0.0))
        pixel_count = float(stats_t2_info.get("BUILTUP_count", 0.0))

        pixel_area_m2 = 10.0 * 10.0
        builtup_area_m2 = builtup_pixel_sum * pixel_area_m2
        plot_geom = to_shape(plot.approved_layout_geom)
        plot_area_m2 = _area_m2(plot_geom)
        vacant_area_m2 = max(plot_area_m2 - builtup_area_m2, 0.0)

        builtup_pct = (builtup_area_m2 / plot_area_m2) * 100.0 if plot_area_m2 > 0 else 0.0
        vacant_pct = (vacant_area_m2 / plot_area_m2) * 100.0 if plot_area_m2 > 0 else 0.0

        # Encroachment detection: built-up outside approved plot boundary but within area
        builtup_vector = builtup_t2_mask.selfMask().reduceToVectors(
            geometry=ee_aoi,
            scale=10,
            geometryType="polygon",
            labelProperty="builtup",
            maxPixels=1_000_000,
        )

        builtup_features = builtup_vector.getInfo()["features"]
        encroachment_polygons: list[Polygon] = []
        encroached_area_m2_total = 0.0

        for feat in builtup_features:
            poly = shape(feat["geometry"])
            if not poly.is_valid:
                continue

            # Built-up that lies outside the approved plot boundary
            outside = poly.difference(plot_geom)
            # Only consider outside that is still within the industrial area
            outside = outside.intersection(area_geom)
            if outside.is_empty:
                continue

            if isinstance(outside, (Polygon, MultiPolygon)):
                encroached_area_m2_total += _area_m2(outside)
                if isinstance(outside, Polygon):
                    encroachment_polygons.append(outside)
                else:
                    encroachment_polygons.extend(list(outside.geoms))

        encroachment_pct = (
            (encroached_area_m2_total / plot_area_m2) * 100.0 if plot_area_m2 > 0 else 0.0
        )

        # Risk scoring
        (
            is_vacant,
            is_partial,
            is_closed,
            risk_level,
            risk_score,
            recommended_action,
        ) = _compute_risk_flags_and_score(builtup_pct, vacant_pct, encroachment_pct)

        # Road alignment deviation
        road_deviation_m = _detect_road_alignment_deviation(
            plot.approved_road_centerlines, encroachment_polygons
        )

        # NDVI / NDBI statistics for dashboard & PDF
        ndvi_stats = composite_t2.select("NDVI").reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_plot_geom,
            scale=10,
            maxPixels=1_000_000,
        )
        ndbi_stats = composite_t2.select("NDBI").reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_plot_geom,
            scale=10,
            maxPixels=1_000_000,
        )
        mean_ndvi = float(ndvi_stats.getInfo().get("NDVI", 0.0))
        mean_ndbi = float(ndbi_stats.getInfo().get("NDBI", 0.0))

        plot_result = PlotAnalysisResult(
            plot_id=plot.id,
            satellite_run_id=satellite_run.id,
            built_up_area_m2=builtup_area_m2,
            plot_area_m2=plot_area_m2,
            vacant_area_m2=vacant_area_m2,
            encroached_area_m2=encroached_area_m2_total,
            road_alignment_deviation_m=road_deviation_m,
            built_up_percentage=builtup_pct,
            vacant_percentage=vacant_pct,
            is_vacant=is_vacant,
            is_partial_construction=is_partial,
            is_closed=is_closed,
            has_encroachment=encroachment_pct > 0.0,
            risk_score=risk_score,
            risk_level=risk_level,
            recommended_action=recommended_action,
            mean_ndvi=mean_ndvi,
            mean_ndbi=mean_ndbi,
            raw_stats={
                "pixel_count": pixel_count,
                "builtup_pixels": builtup_pixel_sum,
                "vegetation_pixels": vegetation_pixel_sum,
                "encroachment_pct": encroachment_pct,
            },
        )
        db.add(plot_result)

        # Persist encroachment polygons
        for enc_poly in encroachment_polygons:
            enc = EncroachmentPolygon(
                plot_id=plot.id,
                satellite_run_id=satellite_run.id,
                geom=f"SRID=4326;{enc_poly.wkt}",
                encroached_area_m2=_area_m2(enc_poly),
                encroachment_type="builtup_outside_boundary",
            )
            db.add(enc)

        results.append((plot_result, plot))

    db.commit()

    return results


