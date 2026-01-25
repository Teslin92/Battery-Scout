"""
Battery Scout - FastAPI Backend
API endpoints for React frontend subscription management
Uses Supabase for data persistence
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import os

from utils import (
    save_subscriber,
    verify_unsubscribe_token,
    remove_subscriber,
    validate_subscription,
    TECH_TOPICS,
    POLICY_TOPICS,
    SUPPLY_TOPICS,
    ALL_CATEGORIES,
)
from supabase_client import (
    get_recent_articles,
    get_subscriber_count,
)


# --- PYDANTIC MODELS ---

class SignupRequest(BaseModel):
    email: EmailStr
    topics: List[str] = Field(..., min_length=1, description="At least one topic required")
    frequency: str = Field(..., pattern="^(daily|weekly|Daily|Weekly)$", description="Must be 'daily' or 'weekly'")
    regions: Optional[List[str]] = Field(default=None, description="Region preferences: North America, Europe, Asia, or Global")


class SignupResponse(BaseModel):
    success: bool
    message: str


class UnsubscribeVerifyRequest(BaseModel):
    token: str


class UnsubscribeVerifyResponse(BaseModel):
    valid: bool
    email: Optional[str] = None
    message: str


class UnsubscribeConfirmRequest(BaseModel):
    email: EmailStr


class UnsubscribeConfirmResponse(BaseModel):
    success: bool
    message: str


class TopicsResponse(BaseModel):
    tech_topics: List[str]
    policy_topics: List[str]
    supply_topics: List[str]
    all_categories: List[str]


class ContentItem(BaseModel):
    title: str
    summary: str
    category: str
    source_name: Optional[str] = None
    source_country: Optional[str] = None
    url: Optional[str] = None


class ContentResponse(BaseModel):
    sample_articles: List[ContentItem]


class StatsResponse(BaseModel):
    total_subscribers: int
    active_subscribers: int
    daily_subscribers: int
    weekly_subscribers: int


# --- FASTAPI APP INITIALIZATION ---

app = FastAPI(
    title="Battery Scout API",
    description="Backend API for Battery Scout newsletter subscription service",
    version="2.0.0"
)


# --- CORS CONFIGURATION ---

# Allow requests from React dev servers and production domains
origins = [
    "http://localhost:3000",      # React dev (Create React App)
    "http://localhost:5173",      # Vite dev
    "http://localhost:5174",      # Vite dev (alternate port)
    "http://localhost:8080",      # Vite dev (this project's port)
    "https://battery-scout.streamlit.app",  # Legacy Streamlit app
]

# Get production frontend URL from environment variable
production_frontend_url = os.environ.get("FRONTEND_URL")
if production_frontend_url:
    origins.append(production_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.(vercel\.app|netlify\.app)",  # Match Vercel and Netlify subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API ENDPOINTS ---

@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Battery Scout API",
        "version": "2.0.0",
        "database": "Supabase"
    }


@app.get("/api/topics", response_model=TopicsResponse, tags=["Topics"])
async def get_topics():
    """
    Get available topic categories for subscription.

    Returns organized topic categories:
    - Technology & Innovation
    - Policy & Regulations
    - Supply Chain & Materials
    """
    return TopicsResponse(
        tech_topics=TECH_TOPICS,
        policy_topics=POLICY_TOPICS,
        supply_topics=SUPPLY_TOPICS,
        all_categories=ALL_CATEGORIES
    )


@app.post("/api/signup", response_model=SignupResponse, tags=["Subscription"])
async def signup(request: SignupRequest):
    """
    Subscribe a user to Battery Scout email updates.

    - **email**: Valid email address
    - **topics**: List of topic names (at least 1 required)
    - **frequency**: "daily" or "weekly"
    """
    # Validate subscription
    is_valid, error_message = validate_subscription(request.email, request.topics)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Save subscriber to Supabase
    success, error = save_subscriber(
        request.email,
        request.topics,
        request.frequency,
        request.regions  # Can be None, will default to ["Global"]
    )

    if success:
        freq_lower = request.frequency.lower()
        if freq_lower == "daily":
            message = f"Success! You're subscribed to {len(request.topics)} topic(s). Check your inbox tomorrow for your first daily update."
        else:
            message = f"Success! You're subscribed to {len(request.topics)} topic(s). Check your inbox next Monday for your first weekly digest."

        return SignupResponse(success=True, message=message)
    else:
        # Check if it's a duplicate email error
        if error and "already subscribed" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error or "Failed to save subscription"
        )


@app.post("/api/unsubscribe/verify", response_model=UnsubscribeVerifyResponse, tags=["Unsubscribe"])
async def verify_unsubscribe(request: UnsubscribeVerifyRequest):
    """
    Verify an unsubscribe token and extract the email address.

    - **token**: Unsubscribe token from email link
    """
    email = verify_unsubscribe_token(request.token)

    if email:
        return UnsubscribeVerifyResponse(
            valid=True,
            email=email,
            message=f"Token verified for {email}"
        )
    else:
        return UnsubscribeVerifyResponse(
            valid=False,
            email=None,
            message="Invalid or expired unsubscribe token"
        )


@app.post("/api/unsubscribe/confirm", response_model=UnsubscribeConfirmResponse, tags=["Unsubscribe"])
async def confirm_unsubscribe(request: UnsubscribeConfirmRequest):
    """
    Confirm unsubscribe and deactivate subscriber.

    - **email**: Email address to unsubscribe
    """
    success, error = remove_subscriber(request.email)

    if success:
        return UnsubscribeConfirmResponse(
            success=True,
            message="You've been successfully unsubscribed. Sorry to see you go!"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error or "Email not found in subscriber list"
        )


@app.get("/api/content", response_model=ContentResponse, tags=["Content"])
async def get_sample_content():
    """
    Get sample content for landing page preview.

    Returns recent articles from Supabase or static examples if none available.
    """
    try:
        # Try to get recent articles from Supabase
        recent = get_recent_articles(hours=48)

        if recent and len(recent) >= 3:
            sample_articles = [
                ContentItem(
                    title=article["title"],
                    summary=article.get("summary", ""),
                    category=article["category"],
                    source_name=article.get("source_name"),
                    source_country=article.get("source_country"),
                    url=article.get("url")
                )
                for article in recent[:3]
            ]
            return ContentResponse(sample_articles=sample_articles)
    except Exception as e:
        # Log error instead of silently swallowing it
        # This helps with debugging production issues
        print(f"⚠️  Warning: Failed to fetch recent articles for sample content: {e}")
        print(f"   Falling back to static content")
        # Fall back to static content

    # Static fallback content
    sample_articles = [
        ContentItem(
            title="QuantumScape announces breakthrough in solid-state battery production",
            summary="QuantumScape achieved 95% yield in their pilot production line using a new ceramic separator process, targeting 10 GWh annual capacity by 2027 for automotive applications.",
            category="Technology & Innovation"
        ),
        ContentItem(
            title="DOE announces $2B in battery manufacturing grants",
            summary="The Department of Energy allocated $2 billion across 15 projects to build domestic battery manufacturing capacity, prioritizing LFP and solid-state technologies with expected job creation of 8,000 positions.",
            category="Policy & Regulations"
        ),
        ContentItem(
            title="CATL unveils sodium-ion battery with 200 Wh/kg energy density",
            summary="Chinese Update: CATL's third-generation sodium-ion battery reaches 200 Wh/kg, targeting budget EVs and energy storage with commercial production starting Q3 2026.",
            category="Technology & Innovation"
        )
    ]

    return ContentResponse(sample_articles=sample_articles)


@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats():
    """
    Get subscriber statistics.

    Returns count of total, active, daily, and weekly subscribers.
    """
    try:
        stats = get_subscriber_count()
        return StatsResponse(
            total_subscribers=stats["total"],
            active_subscribers=stats["active"],
            daily_subscribers=stats["daily"],
            weekly_subscribers=stats["weekly"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {e}"
        )


# --- MAIN ---

if __name__ == "__main__":
    import uvicorn

    # Get port from environment variable (Railway sets PORT)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
