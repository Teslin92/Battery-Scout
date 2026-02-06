"""Quick script to check if articles have summaries in the database."""
import os
from supabase_client import get_supabase_client

def check_summaries():
    supabase = get_supabase_client()

    # Get recent articles
    response = supabase.table("articles").select("title, summary, created_at").order("created_at", desc=True).limit(10).execute()

    print(f"Found {len(response.data)} recent articles:\n")

    for i, article in enumerate(response.data, 1):
        title = article.get("title", "No title")[:60]
        summary = article.get("summary", "")
        created = article.get("created_at", "")[:10]

        has_summary = "✅" if summary else "❌"
        summary_preview = summary[:80] + "..." if summary and len(summary) > 80 else summary or "(empty)"

        print(f"{i}. {has_summary} [{created}] {title}")
        print(f"   Summary: {summary_preview}\n")

if __name__ == "__main__":
    check_summaries()
