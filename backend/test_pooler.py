"""Test connection using Supabase Connection Pooler (port 6543)"""
import psycopg2

# Try connection pooler instead of direct connection
# Connection pooler uses port 6543 which might not be blocked

print("Testing Supabase Connection Pooler...")
print("=" * 60)

# You need to get the pooler connection string from Supabase
# Go to: Settings -> Database -> Connection Pooling

# For now, let's try the direct connection with IPv6
try:
    # First, try with IPv6 address directly
    print("\nAttempt 1: Using IPv6 address directly...")
    conn = psycopg2.connect(
        host="2406:da1a:6b0:f620:f352:c961:f380:d57c",
        port="5432",
        database="postgres",
        user="postgres",
        password="$$$Kodandam999",
        connect_timeout=10
    )
    print("SUCCESS with IPv6!")
    conn.close()
    
except Exception as e:
    print(f"IPv6 failed: {e}")
    
    # Try with hostname and different timeout
    try:
        print("\nAttempt 2: Using hostname with longer timeout...")
        conn = psycopg2.connect(
            host="db.ehfuxdzryfqcshsmjdgz.supabase.co",
            port="5432",
            database="postgres",
            user="postgres",
            password="$$$Kodandam999",
            connect_timeout=30
        )
        print("SUCCESS with hostname!")
        conn.close()
        
    except Exception as e2:
        print(f"Hostname also failed: {e2}")
        print("\n" + "=" * 60)
        print("DIAGNOSIS: Port 5432 appears to be blocked")
        print("\nSOLUTION: Use Supabase Connection Pooler")
        print("\nSteps:")
        print("1. Go to Supabase Dashboard")
        print("2. Settings -> Database")
        print("3. Find 'Connection Pooling' section")
        print("4. Copy the pooler connection string")
        print("5. Update .env with pooler details:")
        print("   - Different host (pooler.supabase.com)")
        print("   - Different port (6543)")
        print("   - Different user format (postgres.projectref)")
        print("=" * 60)
