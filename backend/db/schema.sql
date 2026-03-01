CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE industrial_areas (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    boundary geometry(MULTIPOLYGON, 4326) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE plots (
    id UUID PRIMARY KEY,
    industrial_area_id UUID NOT NULL REFERENCES industrial_areas(id) ON DELETE CASCADE,
    plot_number TEXT NOT NULL,
    approved_land_use TEXT,
    approved_layout_geom geometry(MULTIPOLYGON, 4326) NOT NULL,
    approved_road_centerlines geometry(MULTILINESTRING, 4326),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE satellite_runs (
    id UUID PRIMARY KEY,
    industrial_area_id UUID NOT NULL REFERENCES industrial_areas(id) ON DELETE CASCADE,
    run_type TEXT NOT NULL,
    t1_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    t2_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    sentinel_collection TEXT DEFAULT 'COPERNICUS/S2_SR_HARMONIZED',
    cloud_coverage_threshold DOUBLE PRECISION DEFAULT 40.0,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    finished_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE plot_analysis_results (
    id UUID PRIMARY KEY,
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    satellite_run_id UUID NOT NULL REFERENCES satellite_runs(id) ON DELETE CASCADE,
    built_up_area_m2 DOUBLE PRECISION NOT NULL,
    plot_area_m2 DOUBLE PRECISION NOT NULL,
    vacant_area_m2 DOUBLE PRECISION NOT NULL,
    encroached_area_m2 DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    road_alignment_deviation_m DOUBLE PRECISION,
    built_up_percentage DOUBLE PRECISION NOT NULL,
    vacant_percentage DOUBLE PRECISION NOT NULL,
    is_vacant BOOLEAN NOT NULL DEFAULT FALSE,
    is_partial_construction BOOLEAN NOT NULL DEFAULT FALSE,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    has_encroachment BOOLEAN NOT NULL DEFAULT FALSE,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_level TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    mean_ndvi DOUBLE PRECISION,
    mean_ndbi DOUBLE PRECISION,
    raw_stats JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE encroachment_polygons (
    id UUID PRIMARY KEY,
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    satellite_run_id UUID NOT NULL REFERENCES satellite_runs(id) ON DELETE CASCADE,
    geom geometry(MULTIPOLYGON, 4326) NOT NULL,
    encroached_area_m2 DOUBLE PRECISION NOT NULL,
    encroachment_type TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE INDEX idx_plots_industrial_area ON plots(industrial_area_id);
CREATE INDEX idx_runs_industrial_area ON satellite_runs(industrial_area_id);
CREATE INDEX idx_results_plot ON plot_analysis_results(plot_id);
CREATE INDEX idx_results_run ON plot_analysis_results(satellite_run_id);
CREATE INDEX idx_encroachments_plot ON encroachment_polygons(plot_id);
CREATE INDEX idx_encroachments_run ON encroachment_polygons(satellite_run_id);


