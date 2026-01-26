"""
Battery Scout - Supabase Database Client
Handles all database operations using Supabase instead of Google Sheets.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from supabase import create_client, Client


# --- SUPABASE CONNECTION ---

def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client instance.

    Environment variables required:
        - SUPABASE_URL: Your Supabase project URL
        - SUPABASE_SERVICE_KEY: Service role key for backend operations

    Returns:
        Client: Authenticated Supabase client

    Raises:
        ValueError: If environment variables are not set
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables."
        )

    return create_client(supabase_url, supabase_key)


# --- CATEGORY MAPPING ---
# New 6-category system with topic-based organization

# Database column names for category preferences
CATEGORY_PREF_COLUMNS = {
    "Companies & Deals": "pref_companies_deals",
    "Policy & Regulation": "pref_policy_regulation",
    "Supply Chain": "pref_supply_chain",
    "Lithium-ion & Solid-state": "pref_lithium_solidstate",
    "Sodium-ion & Alternatives": "pref_sodium_alternatives",
    "Recycling & Second-life": "pref_recycling",
}

NEW_CATEGORIES = [
    "Companies & Deals",
    "Policy & Regulation",
    "Supply Chain",
    "Lithium-ion & Solid-state",
    "Sodium-ion & Alternatives",
    "Recycling & Second-life",
]

# Region preferences for filtering international news
AVAILABLE_REGIONS = [
    "North America",  # US, Canada
    "Europe",         # EU, UK, etc.
    "Asia",           # China, Japan, Korea, etc.
    "Global",         # Include all regions
]

# Maps source_country codes to regions
COUNTRY_TO_REGION = {
    # North America
    "US": "North America",
    "CA": "North America",
    "MX": "North America",
    # Europe
    "DE": "Europe",
    "FR": "Europe",
    "UK": "Europe",
    "GB": "Europe",
    "SE": "Europe",
    "HU": "Europe",
    "ES": "Europe",
    "IT": "Europe",
    "NL": "Europe",
    "PL": "Europe",
    "NO": "Europe",
    "FI": "Europe",
    # Asia
    "CN": "Asia",
    "JP": "Asia",
    "KR": "Asia",
    "IN": "Asia",
    "TW": "Asia",
    "TH": "Asia",
    "VN": "Asia",
    "ID": "Asia",
    "AU": "Asia",  # Grouping with Asia-Pacific
}

# Legacy mapping for old subscribers
OLD_TO_NEW_CATEGORY_MAP = {
    # Map old categories to new ones
    "Next-Gen Batteries": "Lithium-ion & Solid-state",
    "Advanced Materials": "Lithium-ion & Solid-state",
    "Battery Safety & Performance": "Lithium-ion & Solid-state",
    "Critical Minerals & Mining": "Supply Chain",
    "Manufacturing & Gigafactories": "Companies & Deals",
    "Energy Storage Systems": "Sodium-ion & Alternatives",
    "US Policy & Incentives": "Policy & Regulation",
    "EU Regulations": "Policy & Regulation",
    "China Industry & Trade": "Policy & Regulation",
    "Recycling & Circular Economy": "Recycling & Second-life",
    "Technology & Innovation": "Lithium-ion & Solid-state",
    "Supply Chain & Materials": "Supply Chain",
    "Manufacturing & Production": "Companies & Deals",
    "Policy & Regulations": "Policy & Regulation",
    "Battery Recycling": "Recycling & Second-life",
    "Industry News": "Companies & Deals",
    "Market Applications": "Companies & Deals",
}


def map_old_categories_to_new(old_categories: List[str]) -> List[str]:
    """
    Maps old 10-category names to new 7-category names.

    Args:
        old_categories: List of old category names

    Returns:
        List of new category names (deduplicated)
    """
    new_categories = set()
    for old_cat in old_categories:
        if old_cat in OLD_TO_NEW_CATEGORY_MAP:
            new_categories.add(OLD_TO_NEW_CATEGORY_MAP[old_cat])
        elif old_cat in NEW_CATEGORIES:
            # Already a new category
            new_categories.add(old_cat)
        else:
            # Default to Industry News for unknown categories
            new_categories.add("Industry News")
    return list(new_categories)


# --- SUBSCRIBER OPERATIONS ---

def get_active_subscribers() -> List[Dict[str, Any]]:
    """
    Fetches all active subscribers with their preferences.
    Converts boolean preference columns to a categories list.

    Returns:
        List of subscriber dictionaries with keys:
            - id: UUID
            - email: str
            - frequency: str ("daily" or "weekly")
            - categories: List[str] (built from pref_* columns)
            - subscribed_at: datetime
            - is_active: bool
    """
    supabase = get_supabase_client()

    response = supabase.table("subscribers").select("*").eq("is_active", True).execute()

    # Convert boolean pref columns to categories list
    subscribers = []
    for sub in response.data:
        # Build categories from preference columns
        categories = []
        for cat_name, col_name in CATEGORY_PREF_COLUMNS.items():
            # Only include category if preference column is explicitly True
            # Default to False if column doesn't exist (not True)
            if sub.get(col_name, False) is True:
                categories.append(cat_name)

        # If subscriber has old-style categories array, convert them
        if not categories and sub.get("categories"):
            old_cats = sub.get("categories", [])
            categories = list(set(
                OLD_TO_NEW_CATEGORY_MAP.get(c, c) for c in old_cats
                if OLD_TO_NEW_CATEGORY_MAP.get(c, c) in NEW_CATEGORIES
            ))

        # If still no categories, give them all
        if not categories:
            categories = NEW_CATEGORIES.copy()

        sub["categories"] = categories

        # Handle regions - default to Global if not set
        regions = sub.get("regions", [])
        if not regions or "Global" in regions:
            regions = ["Global"]  # Global means all regions
        sub["regions"] = regions

        subscribers.append(sub)

    return subscribers


def get_subscribers_by_frequency(frequency: str) -> List[Dict[str, Any]]:
    """
    Fetches active subscribers filtered by email frequency preference.

    Args:
        frequency: Email frequency ("daily" or "weekly")

    Returns:
        List of subscriber dictionaries matching the frequency
    """
    supabase = get_supabase_client()

    # Supabase stores frequency in lowercase
    freq_lower = frequency.lower()

    response = (
        supabase.table("subscribers")
        .select("*")
        .eq("is_active", True)
        .eq("frequency", freq_lower)
        .execute()
    )

    return response.data


def get_subscriber_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single subscriber by email address.

    Args:
        email: Subscriber's email address

    Returns:
        Subscriber dictionary if found, None otherwise
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("subscribers")
        .select("*")
        .eq("email", email.lower())
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]
    return None


def save_subscriber(
    email: str,
    categories: List[str],
    frequency: str,
    regions: Optional[List[str]] = None
) -> tuple[bool, Optional[str]]:
    """
    Saves a new subscriber to the database.

    Args:
        email: Subscriber's email address
        categories: List of category names
        frequency: Email frequency ("daily" or "weekly")
        regions: List of region preferences (optional, defaults to ["Global"])

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    supabase = get_supabase_client()

    # Default to Global if no regions specified
    if not regions:
        regions = ["Global"]

    try:
        # Build preference columns based on selected categories
        # Initialize all preferences to False
        pref_data = {
            "pref_companies_deals": False,
            "pref_policy_regulation": False,
            "pref_supply_chain": False,
            "pref_lithium_solidstate": False,
            "pref_sodium_alternatives": False,
            "pref_recycling": False,
        }
        
        # Set to True only for selected categories
        for category in categories:
            if category in CATEGORY_PREF_COLUMNS:
                col_name = CATEGORY_PREF_COLUMNS[category]
                pref_data[col_name] = True
        
        # Build region preference columns
        # Initialize all region preferences to False
        region_pref_data = {
            "pref_north_america": False,
            "pref_europe": False,
            "pref_asia": False,
            "pref_global": False,
        }
        
        # Set to True only for selected regions
        if regions:
            for region in regions:
                region_normalized = region.strip()
                if region_normalized == "North America":
                    region_pref_data["pref_north_america"] = True
                elif region_normalized == "Europe":
                    region_pref_data["pref_europe"] = True
                elif region_normalized == "Asia":
                    region_pref_data["pref_asia"] = True
                elif region_normalized == "Global":
                    region_pref_data["pref_global"] = True
        
        # Merge region preferences into pref_data
        pref_data.update(region_pref_data)

        # Check if subscriber already exists
        existing = get_subscriber_by_email(email)

        if existing:
            if existing["is_active"]:
                return False, "This email is already subscribed."
            else:
                # Reactivate subscriber with new preferences
                update_data = {
                    "is_active": True,
                    "categories": categories,
                    "frequency": frequency.lower(),
                    "regions": regions,
                    "subscribed_at": datetime.now(timezone.utc).isoformat(),
                    **pref_data  # Include preference columns
                }
                supabase.table("subscribers").update(update_data).eq("email", email.lower()).execute()
                return True, None

        # Insert new subscriber with preference columns
        insert_data = {
            "email": email.lower(),
            "categories": categories,
            "frequency": frequency.lower(),
            "regions": regions,
            "is_active": True,
            **pref_data  # Include preference columns
        }
        supabase.table("subscribers").insert(insert_data).execute()

        return True, None

    except Exception as e:
        return False, f"Error saving subscriber: {e}"


def deactivate_subscriber(email: str) -> tuple[bool, Optional[str]]:
    """
    Deactivates a subscriber by setting is_active=false.
    This is a soft delete that preserves the record.

    Args:
        email: Email address to deactivate

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    supabase = get_supabase_client()

    try:
        # Check if subscriber exists
        existing = get_subscriber_by_email(email)

        if not existing:
            return False, "Email not found in subscriber list"

        if not existing["is_active"]:
            return False, "Subscriber is already unsubscribed"

        # Soft delete by setting is_active to false
        supabase.table("subscribers").update({
            "is_active": False
        }).eq("email", email.lower()).execute()

        return True, None

    except Exception as e:
        return False, f"Error deactivating subscriber: {e}"


def update_subscriber_preferences(
    email: str,
    categories: Optional[List[str]] = None,
    frequency: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Updates a subscriber's preferences.

    Args:
        email: Subscriber's email address
        categories: New list of categories (optional)
        frequency: New frequency preference (optional)

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    supabase = get_supabase_client()

    try:
        existing = get_subscriber_by_email(email)

        if not existing:
            return False, "Subscriber not found"

        update_data = {}
        if categories is not None:
            update_data["categories"] = categories
            
            # Update preference columns based on categories
            # Initialize all to False
            pref_data = {
                "pref_companies_deals": False,
                "pref_policy_regulation": False,
                "pref_supply_chain": False,
                "pref_lithium_solidstate": False,
                "pref_sodium_alternatives": False,
                "pref_recycling": False,
            }
            
            # Set to True only for selected categories
            for category in categories:
                if category in CATEGORY_PREF_COLUMNS:
                    col_name = CATEGORY_PREF_COLUMNS[category]
                    pref_data[col_name] = True
            
            update_data.update(pref_data)
            
        if frequency is not None:
            update_data["frequency"] = frequency.lower()

        if not update_data:
            return False, "No updates provided"

        supabase.table("subscribers").update(update_data).eq("email", email.lower()).execute()

        return True, None

    except Exception as e:
        return False, f"Error updating subscriber: {e}"


# --- ARTICLE OPERATIONS ---

def save_article(article_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Saves a scraped article to the articles table.

    Args:
        article_data: Dictionary containing:
            - title: str
            - url: str
            - summary: str (AI-generated summary)
            - category: str
            - source_country: str (e.g., "US", "CN", "DE")
            - source_name: str (e.g., "Reuters", "Bloomberg")
            - publish_date: datetime or str

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    supabase = get_supabase_client()

    try:
        # Normalize publish_date to ISO string
        pub_date = article_data.get("publish_date")
        if isinstance(pub_date, datetime):
            pub_date = pub_date.isoformat()

        supabase.table("articles").insert({
            "title": article_data["title"],
            "url": article_data["url"],
            "summary": article_data.get("summary", ""),
            "category": article_data["category"],
            "source_country": article_data.get("source_country", "US"),
            "source_name": article_data.get("source_name", "Unknown"),
            "publish_date": pub_date
        }).execute()

        return True, None

    except Exception as e:
        # Handle duplicate URL errors gracefully
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return True, None  # Already exists, not an error
        return False, f"Error saving article: {e}"


def get_recent_articles(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Retrieves articles from the last N hours.

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        List of article dictionaries
    """
    supabase = get_supabase_client()

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    response = (
        supabase.table("articles")
        .select("*")
        .gte("created_at", cutoff_time.isoformat())
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_articles_by_category(
    category: str,
    hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Retrieves recent articles filtered by category.

    Args:
        category: Category name to filter by
        hours: Number of hours to look back (default: 24)

    Returns:
        List of article dictionaries
    """
    supabase = get_supabase_client()

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    response = (
        supabase.table("articles")
        .select("*")
        .eq("category", category)
        .gte("created_at", cutoff_time.isoformat())
        .order("publish_date", desc=True)
        .execute()
    )

    return response.data


def article_exists(url: str) -> bool:
    """
    Checks if an article with the given URL already exists.

    Args:
        url: Article URL to check

    Returns:
        True if article exists, False otherwise
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("articles")
        .select("id")
        .eq("url", url)
        .limit(1)
        .execute()
    )

    return len(response.data) > 0


# --- UTILITY FUNCTIONS ---

def filter_articles_by_regions(
    articles: List[Dict[str, Any]],
    regions: List[str]
) -> List[Dict[str, Any]]:
    """
    Filters articles based on subscriber's region preferences.

    Args:
        articles: List of article dictionaries
        regions: List of region names (e.g., ["North America", "Europe"])

    Returns:
        Filtered list of articles matching the regions
    """
    # If Global is in regions, return all articles
    if "Global" in regions:
        return articles

    filtered = []
    for article in articles:
        country_code = article.get("source_country", "US")
        article_region = COUNTRY_TO_REGION.get(country_code, "North America")

        if article_region in regions:
            filtered.append(article)

    return filtered


def get_subscriber_count() -> Dict[str, int]:
    """
    Returns subscriber statistics.

    Returns:
        Dictionary with keys:
            - total: Total subscribers
            - active: Active subscribers
            - daily: Daily frequency subscribers
            - weekly: Weekly frequency subscribers
    """
    supabase = get_supabase_client()

    # Get all subscribers
    all_subs = supabase.table("subscribers").select("is_active, frequency").execute()

    stats = {
        "total": len(all_subs.data),
        "active": 0,
        "daily": 0,
        "weekly": 0
    }

    for sub in all_subs.data:
        if sub["is_active"]:
            stats["active"] += 1
            if sub["frequency"] == "daily":
                stats["daily"] += 1
            elif sub["frequency"] == "weekly":
                stats["weekly"] += 1

    return stats
