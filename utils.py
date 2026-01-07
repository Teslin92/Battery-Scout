"""
Battery Scout - Utility Functions
Contains all business logic, API calls, and data processing functions.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
import base64
from typing import List, Optional, Dict, Any

# --- CONFIGURATION ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "Battery Subscribers"

# --- TOPIC CATEGORIES ---
TECH_TOPICS = [
    "Next-Gen Batteries",
    "Advanced Materials",
    "Energy Storage Systems",
    "Battery Safety & Performance"
]

POLICY_TOPICS = [
    "US Policy & Incentives",
    "EU Regulations",
    "China Industry & Trade"
]

SUPPLY_TOPICS = [
    "Critical Minerals & Mining",
    "Manufacturing & Gigafactories",
    "Recycling & Circular Economy"
]


# --- GOOGLE SHEETS FUNCTIONS ---

def get_sheet(secrets: Dict[str, Any]):
    """
    Connects to Google Sheets using service account credentials.

    Args:
        secrets: Dictionary containing 'gcp_service_account' credentials

    Returns:
        gspread.Worksheet: The first worksheet of the Battery Subscribers sheet

    Raises:
        Exception: If connection to Google Sheets fails
    """
    creds_dict = secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def save_subscriber(email: str, topics: List[str], frequency: str, secrets: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Saves a new subscriber to the Google Sheet.

    Args:
        email: Subscriber's email address
        topics: List of topic names the subscriber is interested in
        frequency: Email frequency ('Daily' or 'Weekly')
        secrets: Dictionary containing credentials

    Returns:
        tuple: (success: bool, error_message: Optional[str])
            - (True, None) if save was successful
            - (False, error_message) if save failed
    """
    try:
        sheet = get_sheet(secrets)
        # Convert list ['Lithium', 'Cobalt'] -> string 'Lithium|Cobalt'
        topic_string = "|".join(topics)
        # Sheet structure: Email | Topics | Frequency
        sheet.append_row([email, topic_string, frequency])
        return True, None
    except Exception as e:
        return False, f"Error saving to database: {e}"


def verify_unsubscribe_token(token_string: str, secrets: Dict[str, Any]) -> Optional[str]:
    """
    Verifies an unsubscribe token and extracts the email address.

    Args:
        token_string: Token in format 'base64_email.hash_token'
        secrets: Dictionary containing 'unsubscribe_salt'

    Returns:
        Optional[str]: Email address if token is valid, None otherwise
    """
    try:
        email_encoded, token = token_string.split('.')
        email = base64.urlsafe_b64decode(email_encoded).decode()
        # Verify with same salt as send_email.py
        secret_salt = secrets.get("unsubscribe_salt", "default_salt_change_me")
        expected_token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]
        if token == expected_token:
            return email
    except Exception:
        return None
    return None


def remove_subscriber(email: str, secrets: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Removes a subscriber from the Google Sheet.

    Args:
        email: Email address to remove
        secrets: Dictionary containing credentials

    Returns:
        tuple: (success: bool, error_message: Optional[str])
            - (True, None) if removal was successful
            - (False, error_message) if removal failed or email not found
    """
    try:
        sheet = get_sheet(secrets)
        cell = sheet.find(email)
        if cell:
            sheet.delete_rows(cell.row)
            return True, None
        else:
            return False, "Email not found in subscriber list"
    except Exception as e:
        return False, f"Error removing subscriber: {e}"


# --- VALIDATION FUNCTIONS ---

def validate_email(email: str) -> bool:
    """
    Validates email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email contains '@', False otherwise
    """
    return email and "@" in email


def validate_subscription(email: str, topics: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validates subscription form inputs.

    Args:
        email: Email address
        topics: List of selected topics

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
            - (True, None) if all inputs are valid
            - (False, error_message) if validation fails
    """
    if not email:
        return False, "Please enter your email address."
    elif not validate_email(email):
        return False, "Please enter a valid email address."
    elif not topics:
        return False, "Please select at least one topic."
    return True, None
