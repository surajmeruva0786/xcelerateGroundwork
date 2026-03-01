"""Detailed database connection test with full error output"""
import os
from dotenv import load_dotenv
import traceback

# Load .env file
load_dotenv()

# Print environment variables (without password)
print("=" * 60)
print("Environment variables loaded:")
print("=" * 60)
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
password = os.getenv('POSTGRES_PASSWORD', '')
print(f"POSTGRES_PASSWORD: {'*' * len(password)} ({len(password)} characters)")
print("=" * 60)

# Try to connect
try:
    import psycopg2
    print("\n🔌 Attempting to connect to Supabase...")
    
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        connect_timeout=10
    )
    print("\n✅ CONNECTION SUCCESSFUL!")
    print("=" * 60)
    
    # Test PostgreSQL version
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"PostgreSQL: {version.split(',')[0]}")
    
    # Test PostGIS
    try:
        cur.execute("SELECT PostGIS_Version();")
        postgis_version = cur.fetchone()[0]
        print(f"✅ PostGIS: {postgis_version}")
    except Exception as e:
        print(f"⚠️  PostGIS not enabled yet")
        print(f"   Run this in Supabase SQL Editor:")
        print(f"   CREATE EXTENSION IF NOT EXISTS postgis;")
    
    # Test current database
    cur.execute("SELECT current_database();")
    db_name = cur.fetchone()[0]
    print(f"Database: {db_name}")
    
    cur.close()
    conn.close()
    print("=" * 60)
    print("\n✨ All checks passed! Ready to initialize tables.")
    print("\nNext step:")
    print("   .\\venv\\Scripts\\python.exe init_db.py")
    
except Exception as e:
    print("\n❌ CONNECTION FAILED!")
    print("=" * 60)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\n" + "=" * 60)
    print("FULL ERROR DETAILS:")
    print("=" * 60)
    traceback.print_exc()
    print("=" * 60)
    
    print("\n🔧 TROUBLESHOOTING:")
    print("=" * 60)
    
    if "password authentication failed" in str(e):
        print("❌ Password is incorrect")
        print("   → Check your .env file")
        print("   → Make sure password has no extra spaces")
        print("   → Password is case-sensitive")
    
    elif "timeout" in str(e).lower():
        print("❌ Connection timeout")
        print("   → Check if Supabase project is running (not paused)")
        print("   → Disable VPN if you're using one")
        print("   → Check firewall settings")
    
    elif "could not translate host name" in str(e):
        print("❌ Invalid hostname")
        print("   → Check POSTGRES_HOST in .env file")
        print("   → Should be: db.xxxxx.supabase.co")
    
    else:
        print("❌ Unknown error")
        print("   → Check Supabase project status")
        print("   → Verify all credentials in .env")
        print("   → Try resetting database password in Supabase")
