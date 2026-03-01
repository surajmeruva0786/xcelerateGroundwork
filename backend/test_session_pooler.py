"""Test Session Pooler connection"""
import psycopg2

print("Testing Supabase Session Pooler connection...")
print("=" * 60)

# Session Pooler configuration
host = "aws-0-ap-south-1.pooler.supabase.com"
port = "6543"
database = "postgres"
user = "postgres.ehfuxdzryfqcshsmjdgz"
password = "$$$Kodandam999"

print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        connect_timeout=15
    )
    
    print("\nSUCCESS! Connected via Session Pooler")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"\nPostgreSQL: {version.split(',')[0]}")
    
    # Check PostGIS
    try:
        cur.execute("SELECT PostGIS_Version();")
        postgis_ver = cur.fetchone()[0]
        print(f"PostGIS: {postgis_ver}")
        print("\nDatabase is ready!")
    except Exception as e:
        print("\nPostGIS not enabled yet.")
        print("Enable it in Supabase SQL Editor:")
        print("  CREATE EXTENSION IF NOT EXISTS postgis;")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("NEXT STEP: Initialize database")
    print("Run: .\\venv\\Scripts\\python.exe init_db.py")
    print("=" * 60)
    
except Exception as e:
    print(f"\nConnection failed: {e}")
    print("\nIf this fails, please:")
    print("1. Go to Supabase Settings -> Database")
    print("2. Scroll to 'Connection String' section")
    print("3. Change Method to 'Session pooler'")
    print("4. Copy the exact connection details shown")
