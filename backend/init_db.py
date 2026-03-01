"""
Database initialization script for Industrial Land Compliance Monitoring.

This script:
1. Creates all tables defined in models.py
2. Enables PostGIS extension
3. Optionally loads sample data for testing

Usage:
    python init_db.py
"""

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.models.models import (
    IndustrialArea,
    Plot,
    SatelliteRun,
    PlotAnalysisResult,
    EncroachmentPolygon,
)


def init_database():
    """Initialize the database with PostGIS extension and create all tables."""
    
    print("🔧 Initializing database...")
    
    # Enable PostGIS extension
    print("📍 Enabling PostGIS extension...")
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            print("✅ PostGIS extension enabled")
        except Exception as e:
            print(f"⚠️  PostGIS extension: {e}")
            print("   (This is OK if PostGIS is already enabled)")
    
    # Create all tables
    print("📊 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        print("\nCreated tables:")
        print("  - industrial_areas")
        print("  - plots")
        print("  - satellite_runs")
        print("  - plot_analysis_results")
        print("  - encroachment_polygons")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    
    print("\n✨ Database initialization complete!")
    print("\n📝 Next steps:")
    print("  1. Start the server: uvicorn app.main:app --reload")
    print("  2. Visit API docs: http://localhost:8000/docs")
    print("  3. Add industrial areas and plots via API or database")


if __name__ == "__main__":
    init_database()
