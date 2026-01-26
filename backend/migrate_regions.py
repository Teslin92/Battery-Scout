"""
Migration script to add region preference boolean columns and migrate existing data.

This script:
1. Adds region preference columns (pref_north_america, pref_europe, pref_asia, pref_global)
2. Migrates existing region array data to boolean columns
"""

import os
import sys
from supabase_client import get_supabase_client

def migrate_regions():
    """
    Migrates region preferences from array to boolean columns.
    """
    supabase = get_supabase_client()
    
    print("Fetching all active subscribers...")
    try:
        response = supabase.table("subscribers").select("email, regions").eq("is_active", True).execute()
        subscribers = response.data
        print(f"Found {len(subscribers)} active subscribers\n")
    except Exception as e:
        print(f"❌ Error fetching subscribers: {e}")
        raise
    
    updated_count = 0
    error_count = 0
    
    for subscriber in subscribers:
        email = subscriber.get("email")
        regions = subscriber.get("regions", [])
        
        if not email:
            continue
        
        # Build region preference columns
        region_pref_data = {
            "pref_north_america": False,
            "pref_europe": False,
            "pref_asia": False,
            "pref_global": False,
        }
        
        # Set to True based on regions array
        if regions and len(regions) > 0:
            for region in regions:
                region_normalized = str(region).strip()
                if region_normalized == "North America":
                    region_pref_data["pref_north_america"] = True
                elif region_normalized == "Europe":
                    region_pref_data["pref_europe"] = True
                elif region_normalized == "Asia":
                    region_pref_data["pref_asia"] = True
                elif region_normalized == "Global":
                    region_pref_data["pref_global"] = True
        else:
            # Default to Global if no regions specified
            region_pref_data["pref_global"] = True
        
        try:
            # Update the subscriber with region preference columns
            supabase.table("subscribers").update(region_pref_data).eq("email", email.lower()).execute()
            updated_count += 1
            
            # Show what was set
            selected_regions = []
            if region_pref_data["pref_north_america"]:
                selected_regions.append("North America")
            if region_pref_data["pref_europe"]:
                selected_regions.append("Europe")
            if region_pref_data["pref_asia"]:
                selected_regions.append("Asia")
            if region_pref_data["pref_global"]:
                selected_regions.append("Global")
            
            print(f"✅ Updated {email}: {', '.join(selected_regions) if selected_regions else 'Global (default)'}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error updating {email}: {e}")
    
    print(f"\n📊 Migration complete:")
    print(f"   ✅ Successfully updated: {updated_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📝 Total processed: {len(subscribers)}")

if __name__ == "__main__":
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)
    
    print("🚀 Starting region preference migration...")
    print("   This will add region boolean columns and migrate existing data\n")
    
    try:
        migrate_regions()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
