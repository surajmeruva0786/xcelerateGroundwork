"""Simple connection test without Unicode characters"""
import psycopg2

# Your Supabase credentials
host = "db.ehfuxdzryfqcshsmjdgz.supabase.co"
port = "5432"
database = "postgres"
user = "postgres"
password = "$$$Kodandam999"

print("Testing Supabase connection...")
print("Host:", host)
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        connect_timeout=10
    )
    
    print("\nSUCCESS! Connected to Supabase")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print("\nPostgreSQL version:", version.split(',')[0])
    
    # Check PostGIS
    try:
        cur.execute("SELECT PostGIS_Version();")
        postgis_ver = cur.fetchone()[0]
        print("PostGIS version:", postgis_ver)
        print("\nDatabase is fully configured!")
    except Exception as e:
        print("\nPostGIS NOT enabled yet.")
        print("Run this in Supabase SQL Editor:")
        print("  CREATE EXTENSION IF NOT EXISTS postgis;")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("NEXT STEP: Initialize database tables")
    print("Run: .\\venv\\Scripts\\python.exe init_db.py")
    print("=" * 60)
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print("\nCONNECTION FAILED")
    print("Error:", error_msg)
    print("\n" + "=" * 60)
    
    if "password authentication failed" in error_msg:
        print("ISSUE: Wrong password")
        print("FIX: Check password in Supabase Settings -> Database")
        print("     Update .env file with correct password")
    elif "timeout" in error_msg.lower():
        print("ISSUE: Connection timeout")
        print("FIX: 1. Check if Supabase project is active (not paused)")
        print("     2. Disable VPN if using one")
        print("     3. Check internet connection")
    elif "could not translate host name" in error_msg:
        print("ISSUE: Invalid hostname")
        print("FIX: Check POSTGRES_HOST in .env matches Supabase")
    else:
        print("ISSUE: Unknown connection error")
        print("FIX: 1. Verify Supabase project is running")
        print("     2. Check all credentials in Settings -> Database")
        print("     3. Try resetting database password")
    
    print("=" * 60)
    
except Exception as e:
    print("\nUNEXPECTED ERROR:", str(e))
