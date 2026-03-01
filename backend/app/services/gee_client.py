"""
Google Earth Engine client utilities.

This module encapsulates authentication and provides helpers to construct
Sentinel-2 based NDVI and NDBI products with cloud masking, tailored for
industrial land compliance monitoring.
"""

from __future__ import annotations

from datetime import datetime
from typing import Tuple

import ee

from app.core.config import settings


def initialize_gee() -> None:
    """Initialise the Earth Engine client using a service account.

    This is safe to call multiple times; subsequent calls become no-ops.
    """
    try:
        # If EE is already initialised, this will not raise.
        _ = ee.Number(1).getInfo()
        return
    except Exception:
        credentials = ee.ServiceAccountCredentials(
            settings.GEE_SERVICE_ACCOUNT, settings.GEE_PRIVATE_KEY_PATH
        )
        ee.Initialize(credentials)


def _mask_s2_clouds(image: ee.Image) -> ee.Image:
    """Mask clouds and cirrus using Sentinel-2 SCL band.

    The SCL (Scene Classification Layer) band labels each pixel:
    - 3, 8, 9, 10: cloud / high-probability cloud / cirrus / snow etc.
    We keep only land, vegetation, water, and bare soil pixels.
    """
    scl = image.select("SCL")
    # Allowed SCL classes for analysis (0-11, keep most non-cloud classes)
    good_classes = [4, 5, 6, 7, 11]  # vegetation, bare soil, water etc.
    mask = scl.remap(
        good_classes,
        [1] * len(good_classes),
        0,
    )
    return image.updateMask(mask)


def _add_ndvi(image: ee.Image) -> ee.Image:
    """Compute NDVI = (NIR - RED) / (NIR + RED).

    Sentinel-2:
    - NIR band: B8
    - RED band: B4
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def _add_ndbi(image: ee.Image) -> ee.Image:
    """Compute NDBI = (SWIR - NIR) / (SWIR + NIR).

    Sentinel-2:
    - SWIR band: B11
    - NIR band: B8
    Higher NDBI typically corresponds to built-up / impervious surfaces.
    """
    ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")
    return image.addBands(ndbi)


def build_s2_composite_with_indices(
    aoi: ee.Geometry,
    start_date: datetime,
    end_date: datetime,
) -> ee.Image:
    """Build a cloud-masked Sentinel-2 median composite with NDVI & NDBI.

    - Filters by date and AOI
    - Filters by low cloud coverage at scene level
    - Applies SCL-based per-pixel cloud masking
    - Generates median composite to reduce residual noise
    - Adds NDVI and NDBI bands for analysis
    """
    initialize_gee()

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
        .map(_mask_s2_clouds)
        .map(_add_ndvi)
        .map(_add_ndbi)
    )

    composite = collection.median().clip(aoi)
    return composite


def derive_builtup_and_vegetation_masks(
    composite: ee.Image,
    ndbi_threshold: float = 0.2,
    ndvi_vegetation_threshold: float = 0.3,
) -> Tuple[ee.Image, ee.Image]:
    """Derive built-up and vegetation masks from NDVI / NDBI.

    - Built-up: NDBI above a threshold (impervious surfaces)
    - Vegetation: NDVI above threshold (green cover)

    Thresholds can be tuned per-region using historical ground truth.
    """
    ndbi = composite.select("NDBI")
    ndvi = composite.select("NDVI")

    builtup_mask = ndbi.gt(ndbi_threshold).rename("BUILTUP")
    vegetation_mask = ndvi.gt(ndvi_vegetation_threshold).rename("VEGETATION")

    return builtup_mask, vegetation_mask


