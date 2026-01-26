"""
Migration script to fix preference columns for existing subscribers.

This script:
1. Fetches all active subscribers
2. Reads their 'categories' array (which contains their original selections)
3. Sets pref_* columns to True only for categories in their array
4. Sets all other pref_* columns to False

Run this once to fix existing data after the bug fix.
"""

import os
import sys
from supabase_client import (
    get_supabase_client,
    CATEGORY_PREF_COLUMNS,
    get_active_subscribers
)


def migrate_subscriber_preferences():
    """
    Migrates all existing subscribers to use pref_* columns correctly.
    """
    supabase = get_supabase_client()
    
    # Get all active subscribers
    print("Fetching all active subscribers...")
    subscribers = get_active_subscribers()
    print(f"Found {len(subscribers)} active subscribers")
    
    updated_count = 0
    error_count = 0
    
    for subscriber in subscribers:
        email = subscriber.get("email")
        categories = subscriber.get("categories", [])
        
        if not email:
            print(f"⚠️  Skipping subscriber with no email: {subscriber.get('id')}")
            continue
        
        # Build preference columns based on categories array
        # Initialize all to False
        pref_data = {
            "pref_companies_deals": False,
            "pref_policy_regulation": False,
            "pref_supply_chain": False,
            "pref_lithium_solidstate": False,
            "pref_sodium_alternatives": False,
            "pref_recycling": False,
        }
        
        # Set to True only for categories in their original selection
        categories_set = False
        for category in categories:
            if category in CATEGORY_PREF_COLUMNS:
                col_name = CATEGORY_PREF_COLUMNS[category]
                pref_data[col_name] = True
                categories_set = True
        
        # If no valid categories found, skip (might be old data format)
        if not categories_set and not categories:
            print(f"⚠️  Skipping {email}: No valid categories found")
            continue
        
        try:
            # Update the subscriber with correct preference columns
            supabase.table("subscribers").update(pref_data).eq("email", email.lower()).execute()
            updated_count += 1
            
            # Show what was set
            selected = [cat for cat, col in CATEGORY_PREF_COLUMNS.items() if pref_data[col]]
            print(f"✅ Updated {email}: {', '.join(selected) if selected else 'No categories'}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error updating {email}: {e}")
    
    print(f"\n📊 Migration complete:")
    print(f"   ✅ Successfully updated: {updated_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📝 Total processed: {len(subscribers)}")


if __name__ == "__main__":
    # Check for environment variables
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        print("   Set these environment variables before running the migration")
        sys.exit(1)
    
    print("🚀 Starting preference migration...")
    print("   This will update pref_* columns based on existing categories arrays")
    print("   Press Ctrl+C to cancel\n")
    
    try:
        migrate_subscriber_preferences()
        print("\n✅ Migration completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
