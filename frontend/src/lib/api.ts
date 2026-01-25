/**
 * API Client for Battery Scout Backend
 * Communicates with FastAPI backend instead of direct Supabase calls
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SignupRequest {
  email: string;
  topics: string[];
  frequency: 'daily' | 'weekly';
  regions?: string[];
}

export interface SignupResponse {
  success: boolean;
  message: string;
}

export interface UnsubscribeVerifyRequest {
  token: string;
}

export interface UnsubscribeVerifyResponse {
  valid: boolean;
  email: string | null;
  message: string;
}

export interface UnsubscribeConfirmRequest {
  email: string;
}

export interface UnsubscribeConfirmResponse {
  success: boolean;
  message: string;
}

export interface TopicsResponse {
  tech_topics: string[];
  policy_topics: string[];
  supply_topics: string[];
  all_categories: string[];
}

export interface ContentItem {
  title: string;
  summary: string;
  category: string;
  source_name?: string;
  source_country?: string;
  url?: string;
}

export interface ContentResponse {
  sample_articles: ContentItem[];
}

export interface StatsResponse {
  total_subscribers: number;
  active_subscribers: number;
  daily_subscribers: number;
  weekly_subscribers: number;
}

/**
 * Sign up a new subscriber
 */
export async function signup(data: SignupRequest): Promise<SignupResponse> {
  const response = await fetch(`${API_BASE_URL}/api/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to sign up' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Verify unsubscribe token
 */
export async function verifyUnsubscribeToken(
  token: string
): Promise<UnsubscribeVerifyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/unsubscribe/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    throw new Error('Failed to verify token');
  }

  return response.json();
}

/**
 * Confirm unsubscribe
 */
export async function confirmUnsubscribe(
  email: string
): Promise<UnsubscribeConfirmResponse> {
  const response = await fetch(`${API_BASE_URL}/api/unsubscribe/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to unsubscribe' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get available topics/categories
 */
export async function getTopics(): Promise<TopicsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/topics`);

  if (!response.ok) {
    throw new Error('Failed to fetch topics');
  }

  return response.json();
}

/**
 * Get sample content for preview
 */
export async function getSampleContent(): Promise<ContentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/content`);

  if (!response.ok) {
    throw new Error('Failed to fetch content');
  }

  return response.json();
}

/**
 * Get subscriber statistics
 */
export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);

  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }

  return response.json();
}
