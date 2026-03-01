"""Test connection with URL encoding for special characters in password"""
import urllib.parse

# Your Supabase credentials
host = "db.ehfuxdzryfqcshsmjdgz.supabase.co"
port = "5432"
database = "postgres"
user = "postgres"
password = "$$$Kodandam999"  # Password with special characters

# URL encode the password
encoded_password = urllib.parse.quote_plus(password)

print("Testing connection with special characters in password...")
print(f"Original password: {password}")
print(f"URL-encoded password: {encoded_password}")
print("=" * 60)

# Try connection with psycopg2
try:
    import psycopg2
    
    print("\n🔌 Attempting connection...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,  # psycopg2 handles special chars automatically
        connect_timeout=10
    )
    
    print("✅ CONNECTION SUCCESSFUL!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"\nPostgreSQL: {cur.fetchone()[0].split(',')[0]}")
    
    # Check for PostGIS
    try:
        cur.execute("SELECT PostGIS_Version();")
        print(f"✅ PostGIS: {cur.fetchone()[0]}")
    except:
        print("⚠️  PostGIS not enabled - run: CREATE EXTENSION IF NOT EXISTS postgis;")
    
    cur.close()
    conn.close()
    
    print("\n✨ Database is ready!")
    print("\nNext step: .\\venv\\Scripts\\python.exe init_db.py")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("1. Password might be incorrect")
    print("2. Supabase project might be paused")
    print("3. Check Supabase Settings → Database for correct credentials")
