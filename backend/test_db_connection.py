"""
Quick test script to verify database connection and PostGIS installation.

Usage:
    python test_db_connection.py
"""

from sqlalchemy import text
from app.db.session import engine


def test_connection():
    """Test database connection and PostGIS availability."""
    
    print("🔍 Testing database connection...\n")
    
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("✅ Database connected successfully!")
            print(f"   PostgreSQL version: {version.split(',')[0]}\n")
            
            # Test PostGIS
            try:
                result = conn.execute(text("SELECT PostGIS_Version();"))
                postgis_version = result.fetchone()[0]
                print("✅ PostGIS extension is available!")
                print(f"   PostGIS version: {postgis_version}\n")
            except Exception as e:
                print("❌ PostGIS extension not found!")
                print(f"   Error: {e}")
                print("\n   To fix this, run in your database:")
                print("   CREATE EXTENSION IF NOT EXISTS postgis;\n")
                return False
            
            # Test database name
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"📊 Connected to database: {db_name}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"\n📋 Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n📋 No tables found yet.")
                print("   Run 'python init_db.py' to create tables.")
            
            print("\n✨ All checks passed! Database is ready to use.")
            return True
            
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"   Error: {e}\n")
        print("   Troubleshooting:")
        print("   1. Check if PostgreSQL is running")
        print("   2. Verify .env file has correct credentials")
        print("   3. Ensure database exists")
        print("   4. Check firewall/network settings")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
