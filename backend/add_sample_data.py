"""Add sample data directly to the database"""
import uuid
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import IndustrialArea, Plot
from geoalchemy2.elements import WKTElement

print("=" * 60)
print("Adding Sample Data to Database")
print("=" * 60)

db = SessionLocal()

try:
    # 1. Create Industrial Area
    print("\n1. Creating Industrial Area...")
    
    existing_area = db.query(IndustrialArea).filter(
        IndustrialArea.code == "CSIDC-P1-001"
    ).first()
    
    if existing_area:
        print(f"[OK] Industrial Area already exists: {existing_area.name}")
        area_id = existing_area.id
    else:
        area = IndustrialArea(
            id=uuid.uuid4(),
            name="CSIDC Industrial Estate - Phase 1",
            code="CSIDC-P1-001",
            description="Main industrial development area",
            boundary=WKTElement(
                'MULTIPOLYGON(((78.0 26.0, 78.05 26.0, 78.05 26.05, 78.0 26.05, 78.0 26.0)))',
                srid=4326
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(area)
        db.commit()
        db.refresh(area)
        area_id = area.id
        print(f"[OK] Industrial Area created: {area.name}")
    
    # 2. Create Sample Plots
    print("\n2. Creating Sample Plots...")
    
    plots_data = [
        {
            "plot_number": "PLOT-A-001",
            "approved_land_use": "Manufacturing",
            "wkt": "MULTIPOLYGON(((78.01 26.01, 78.015 26.01, 78.015 26.015, 78.01 26.015, 78.01 26.01)))"
        },
        {
            "plot_number": "PLOT-A-002",
            "approved_land_use": "Warehouse",
            "wkt": "MULTIPOLYGON(((78.02 26.01, 78.025 26.01, 78.025 26.015, 78.02 26.015, 78.02 26.01)))"
        },
        {
            "plot_number": "PLOT-B-001",
            "approved_land_use": "Processing Unit",
            "wkt": "MULTIPOLYGON(((78.01 26.02, 78.015 26.02, 78.015 26.025, 78.01 26.025, 78.01 26.02)))"
        },
        {
            "plot_number": "PLOT-B-002",
            "approved_land_use": "Assembly Plant",
            "wkt": "MULTIPOLYGON(((78.02 26.02, 78.025 26.02, 78.025 26.025, 78.02 26.025, 78.02 26.02)))"
        },
        {
            "plot_number": "PLOT-C-001",
            "approved_land_use": "Storage Facility",
            "wkt": "MULTIPOLYGON(((78.03 26.01, 78.035 26.01, 78.035 26.015, 78.03 26.015, 78.03 26.01)))"
        }
    ]
    
    for plot_data in plots_data:
        existing_plot = db.query(Plot).filter(
            Plot.plot_number == plot_data["plot_number"]
        ).first()
        
        if existing_plot:
            print(f"  [SKIP] Plot {plot_data['plot_number']} already exists")
        else:
            plot = Plot(
                id=uuid.uuid4(),
                industrial_area_id=area_id,
                plot_number=plot_data["plot_number"],
                approved_land_use=plot_data["approved_land_use"],
                approved_layout_geom=WKTElement(plot_data["wkt"], srid=4326),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(plot)
            db.commit()
            print(f"  [OK] Created: {plot_data['plot_number']} ({plot_data['approved_land_use']})")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Sample data added!")
    print("=" * 60)
    
    total_plots = db.query(Plot).count()
    print(f"\nTotal plots in database: {total_plots}")
    print("\nNext steps:")
    print("1. Refresh your dashboard: http://localhost:5173")
    print(f"2. You should see {total_plots} plots on the map")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
