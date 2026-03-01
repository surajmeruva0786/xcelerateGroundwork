"""Test connection with password from environment file"""
import os
from dotenv import load_dotenv
import psycopg2

# Load .env
load_dotenv()

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')

print("Testing connection with .env credentials...")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Database: {database}")
print(f"User: {user}")
print(f"Password length: {len(password)} characters")
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=host,
        port=int(port),
        database=database,
        user=user,
        password=password,
        connect_timeout=20
    )
    
    print("\nSUCCESS! Connected to Supabase via Session Pooler!")
    print("=" * 60)
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"\nPostgreSQL: {version.split(',')[0]}")
    
    # Check PostGIS
    try:
        cur.execute("SELECT PostGIS_Version();")
        postgis_ver = cur.fetchone()[0]
        print(f"PostGIS: {postgis_ver}")
        print("\nDatabase is fully configured!")
    except Exception as e:
        print("\nPostGIS not enabled yet.")
        print("Run in Supabase SQL Editor:")
        print("  CREATE EXTENSION IF NOT EXISTS postgis;")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("READY TO INITIALIZE DATABASE!")
    print("Next step: .\\venv\\Scripts\\python.exe init_db.py")
    print("=" * 60)
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"\nConnection FAILED!")
    print(f"Error: {error_msg}")
    print("\n" + "=" * 60)
    
    if "password authentication failed" in error_msg:
        print("ISSUE: Incorrect password")
        print("\nSOLUTION:")
        print("1. Go to Supabase Settings -> Database")
        print("2. Click 'Reset database password'")
        print("3. Copy the new password")
        print("4. Update POSTGRES_PASSWORD in .env file")
        print("5. Make sure password has NO quotes around it")
        
    elif "Tenant or user not found" in error_msg:
        print("ISSUE: User format might be incorrect")
        print("\nTry changing POSTGRES_USER in .env to:")
        print("  Option 1: postgres")
        print("  Option 2: postgres.ehfuxdzryfqcshsmjdgz")
        
    else:
        print("ISSUE: Connection error")
        print("\nPossible fixes:")
        print("1. Verify password in Supabase dashboard")
        print("2. Check if project is paused (free tier)")
        print("3. Try resetting database password")
    
    print("=" * 60)

except Exception as e:
    print(f"\nUnexpected error: {e}")
