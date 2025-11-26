import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.db import get_connection
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_connection():
    print("\n--- Testing Database Connection ---")
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"   Version: {version}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_search_function():
    print("\n--- Testing 'buscar_recursos' Function ---")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Test 1: Call function directly
            print("1. Calling buscar_recursos('test')...")
            cur.execute("SELECT * FROM buscar_recursos('test') LIMIT 1;")
            row = cur.fetchone()
            print(f"✅ Function call successful. Result: {row}")
            
            # Test 2: Call with empty string
            print("2. Calling buscar_recursos('')...")
            cur.execute("SELECT * FROM buscar_recursos('') LIMIT 1;")
            row = cur.fetchone()
            print(f"✅ Function call (empty) successful. Result: {row}")
            
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        print("\nPOSSIBLE CAUSES:")
        print("1. The function 'buscar_recursos' does not exist in the database.")
        print("   -> Run the SQL provided in the previous message.")
        print("2. Permission denied.")
        print("   -> Check RLS policies or DB user permissions.")
    finally:
        conn.close()

if __name__ == "__main__":
    if test_connection():
        test_search_function()
