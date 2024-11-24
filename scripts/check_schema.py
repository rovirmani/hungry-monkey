import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Get table information
response = supabase.table('operating_hours').select("*", count='exact').limit(1).execute()
print("\nTable Info:")
print(f"Count: {response.count if hasattr(response, 'count') else 'Unknown'}")
print("\nColumns (from first row):")
if response.data:
    for key in response.data[0].keys():
        print(f"- {key}")
else:
    print("No data to infer columns. Please check table exists and has data.")
