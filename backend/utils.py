"""
Battery Scout - Utility Functions
Contains validation, token verification, and subscriber management functions.
Uses Supabase for data persistence.
"""

import hashlib
import base64
import os
from typing import List, Optional, Dict, Any

from supabase_client import (
    save_subscriber as supabase_save_subscriber,
    deactivate_subscriber,
    get_subscriber_by_email,
    NEW_CATEGORIES,
)


# --- TOPIC CATEGORIES (NEW 7-CATEGORY SYSTEM) ---

TECH_TOPICS = [
    "Technology & Innovation",
    "Manufacturing & Production",
]

POLICY_TOPICS = [
    "Policy & Regulations",
    "Industry News",
]

SUPPLY_TOPICS = [
    "Supply Chain & Materials",
    "Battery Recycling",
    "Market Applications",
]

# All categories combined for reference
ALL_CATEGORIES = NEW_CATEGORIES


# --- LEGACY CATEGORY MAPPING ---
# For backward compatibility with old 10-category subscribers

OLD_TO_NEW_CATEGORY_MAP = {
    "Next-Gen Batteries": "Technology & Innovation",
    "Advanced Materials": "Technology & Innovation",
    "Battery Safety & Performance": "Technology & Innovation",
    "Critical Minerals & Mining": "Supply Chain & Materials",
    "Manufacturing & Gigafactories": "Manufacturing & Production",
    "Energy Storage Systems": "Manufacturing & Production",
    "US Policy & Incentives": "Policy & Regulations",
    "EU Regulations": "Policy & Regulations",
    "China Industry & Trade": "Policy & Regulations",
    "Recycling & Circular Economy": "Battery Recycling",
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
            new_categories.add(old_cat)
        else:
            new_categories.add("Industry News")
    return list(new_categories)


# --- SUBSCRIBER FUNCTIONS ---

def save_subscriber(
    email: str,
    topics: List[str],
    frequency: str,
    regions: Optional[List[str]] = None,
    secrets: Optional[Dict[str, Any]] = None  # Kept for backward compatibility
) -> tuple[bool, Optional[str]]:
    """
    Saves a new subscriber to Supabase.

    Args:
        email: Subscriber's email address
        topics: List of topic/category names
        frequency: Email frequency ('Daily' or 'Weekly')
        regions: List of region preferences (optional, defaults to ["Global"])
        secrets: Deprecated - kept for backward compatibility

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    # Normalize frequency to lowercase for Supabase
    freq_lower = frequency.lower()

    # Map old categories to new if needed
    categories = []
    for topic in topics:
        if topic in OLD_TO_NEW_CATEGORY_MAP:
            categories.append(OLD_TO_NEW_CATEGORY_MAP[topic])
        elif topic in NEW_CATEGORIES:
            categories.append(topic)
        else:
            categories.append(topic)

    # Remove duplicates while preserving order
    seen = set()
    unique_categories = []
    for cat in categories:
        if cat not in seen:
            seen.add(cat)
            unique_categories.append(cat)

    return supabase_save_subscriber(email, unique_categories, freq_lower, regions)


def remove_subscriber(
    email: str,
    secrets: Optional[Dict[str, Any]] = None  # Kept for backward compatibility
) -> tuple[bool, Optional[str]]:
    """
    Removes (deactivates) a subscriber from Supabase.
    This is a soft delete that sets is_active=false.

    Args:
        email: Email address to remove
        secrets: Deprecated - kept for backward compatibility

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    return deactivate_subscriber(email)


def subscriber_exists(email: str) -> bool:
    """
    Checks if a subscriber with the given email exists and is active.

    Args:
        email: Email address to check

    Returns:
        True if active subscriber exists, False otherwise
    """
    subscriber = get_subscriber_by_email(email)
    return subscriber is not None and subscriber.get("is_active", False)


# --- TOKEN FUNCTIONS ---

def generate_unsubscribe_token(email: str) -> str:
    """
    Creates a secure unsubscribe token.

    Args:
        email: Subscriber's email address

    Returns:
        Token in format 'base64_email.hash_token'
    """
    secret_salt = os.environ.get("UNSUBSCRIBE_SALT", "default_salt_change_me")
    token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]
    email_encoded = base64.urlsafe_b64encode(email.encode()).decode()
    return f"{email_encoded}.{token}"


def verify_unsubscribe_token(
    token_string: str,
    secrets: Optional[Dict[str, Any]] = None  # Kept for backward compatibility
) -> Optional[str]:
    """
    Verifies an unsubscribe token and extracts the email address.

    Args:
        token_string: Token in format 'base64_email.hash_token'
        secrets: Dictionary containing 'unsubscribe_salt' (optional, uses env var)

    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        email_encoded, token = token_string.split('.')
        email = base64.urlsafe_b64decode(email_encoded).decode()

        # Get salt from secrets dict or environment
        if secrets and "unsubscribe_salt" in secrets:
            secret_salt = secrets["unsubscribe_salt"]
        else:
            secret_salt = os.environ.get("UNSUBSCRIBE_SALT", "default_salt_change_me")

        expected_token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]

        if token == expected_token:
            return email
    except Exception:
        return None
    return None


# --- VALIDATION FUNCTIONS ---

def validate_email(email: str) -> bool:
    """
    Validates email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email has valid format, False otherwise
    """
    if not email:
        return False

    # Basic validation: contains @ and at least one dot after @
    if "@" not in email:
        return False

    local, domain = email.rsplit("@", 1)
    if not local or not domain or "." not in domain:
        return False

    return True


def validate_subscription(email: str, topics: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validates subscription form inputs.

    Args:
        email: Email address
        topics: List of selected topics

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    if not email:
        return False, "Please enter your email address."
    elif not validate_email(email):
        return False, "Please enter a valid email address."
    elif not topics:
        return False, "Please select at least one topic."
    return True, None
