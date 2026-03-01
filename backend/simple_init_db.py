"""Simple database initialization script"""
from sqlalchemy import create_engine, text
from app.db.session import get_database_url
from app.db.base import Base

# Import all models to register them with Base
from app.models.models import (
    IndustrialArea,
    Plot,
    SatelliteRun,
    PlotAnalysisResult,
    EncroachmentPolygon
)

print("=" * 60)
print("Database Initialization")
print("=" * 60)

# Create engine
engine = create_engine(get_database_url(), pool_pre_ping=True)

# Enable PostGIS
print("\nEnabling PostGIS extension...")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    conn.commit()
print("✓ PostGIS enabled")

# Create all tables
print("\nCreating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")
    
    print("\nCreated tables:")
    print("  - industrial_areas")
    print("  - plots")
    print("  - satellite_runs")
    print("  - plot_analysis_results")
    print("  - encroachment_polygons")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    raise

# Verify tables were created
print("\nVerifying tables...")
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))
    tables = [row[0] for row in result.fetchall()]
    print(f"Found {len(tables)} tables in database:")
    for table in tables:
        print(f"  - {table}")

print("\n" + "=" * 60)
print("✓ Database initialization complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Start the server:")
print("   .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
print("2. Visit API docs: http://localhost:8000/docs")
print("=" * 60)
