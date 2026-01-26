# Preference Migration Script

This script fixes existing subscribers in your database by setting their `pref_*` columns based on their original category selections.

## What it does

1. Fetches all active subscribers from Supabase
2. Reads their `categories` array (which contains their original selections)
3. Sets `pref_*` columns to `True` only for categories they originally selected
4. Sets all other `pref_*` columns to `False`

## How to run

### Option 1: Run locally (recommended for testing)

1. Make sure you have the environment variables set:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_SERVICE_KEY="your_service_key"
   ```

2. Run the script:
   ```bash
   cd backend
   python migrate_preferences.py
   ```

### Option 2: Run on Railway (one-time)

1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to the "Deployments" tab
4. Click "New Deploy" or use the Railway CLI
5. Or use Railway's "Run Command" feature:
   ```bash
   python backend/migrate_preferences.py
   ```

### Option 3: Run via Railway CLI

```bash
railway run python backend/migrate_preferences.py
```

## What to expect

The script will:
- Show progress for each subscriber
- Display which categories were set for each subscriber
- Report total updated, errors, and total processed

Example output:
```
🚀 Starting preference migration...
   This will update pref_* columns based on existing categories arrays
   Press Ctrl+C to cancel

Fetching all active subscribers...
Found 25 active subscribers
✅ Updated user1@example.com: Companies & Deals, Policy & Regulation
✅ Updated user2@example.com: Supply Chain, Recycling & Second-life
...

📊 Migration complete:
   ✅ Successfully updated: 25
   ❌ Errors: 0
   📝 Total processed: 25

✅ Migration completed successfully!
```

## Safety

- The script only updates `pref_*` columns, it doesn't delete or modify other data
- It only processes active subscribers (`is_active = true`)
- You can run it multiple times safely (idempotent)
- It preserves the original `categories` array

## Troubleshooting

**Error: "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"**
- Make sure environment variables are set correctly
- Check Railway variables if running on Railway

**Error: "No valid categories found"**
- Some old subscribers might have empty or invalid categories
- These are skipped (not an error)

**Want to test first?**
- You can modify the script to add a `--dry-run` flag
- Or test with a single email first by filtering in the code
