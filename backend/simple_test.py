"""Simple database connection test"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Print environment variables (without password)
print("Environment variables loaded:")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_PASSWORD: {'*' * len(os.getenv('POSTGRES_PASSWORD', ''))}")

# Try to connect
try:
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    print("\n✅ Connection successful!")
    
    # Test PostGIS
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"PostgreSQL version: {cur.fetchone()[0].split(',')[0]}")
    
    try:
        cur.execute("SELECT PostGIS_Version();")
        print(f"✅ PostGIS version: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"❌ PostGIS not available: {e}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if Supabase project is running")
    print("2. Verify credentials in .env file")
    print("3. Check if IP is allowed in Supabase (Database Settings -> Connection Pooling)")
