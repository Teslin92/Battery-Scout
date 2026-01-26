/**
 * API Client for Battery Scout Backend
 * Communicates with FastAPI backend instead of direct Supabase calls
 */

// Remove trailing slash if present to avoid double slashes
const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Remove ALL trailing slashes and whitespace
const API_BASE_URL = rawApiUrl.trim().replace(/\/+$/, '');

// Helper function to construct API URLs without double slashes
function apiUrl(path: string): string {
  const base = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${cleanPath}`;
}

// #region agent log
fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:6',message:'API_BASE_URL initialized',data:{apiBaseUrl:API_BASE_URL,hasEnvVar:!!import.meta.env.VITE_API_URL,envValue:import.meta.env.VITE_API_URL||'undefined'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
// #endregion

// Always log API_BASE_URL to console for debugging (not sensitive)
console.log('[Battery Scout] API Base URL:', API_BASE_URL);
console.log('[Battery Scout] Environment check:', {
  hasEnvVar: !!import.meta.env.VITE_API_URL,
  envValue: import.meta.env.VITE_API_URL || 'NOT SET',
  isProduction: import.meta.env.PROD,
  isDevelopment: import.meta.env.DEV
});

if (!import.meta.env.VITE_API_URL) {
  console.error('[Battery Scout] ❌ CRITICAL: VITE_API_URL not set!');
  console.error('[Battery Scout] Current value:', API_BASE_URL);
  console.error('[Battery Scout] This will NOT work in production!');
  console.error('[Battery Scout] Action required:');
  console.error('  1. Go to Vercel Dashboard → Settings → Environment Variables');
  console.error('  2. Add VITE_API_URL = https://battery-scout-production.up.railway.app');
  console.error('  3. Select "All environments" (Production, Preview, Development)');
  console.error('  4. Click Save');
  console.error('  5. Go to Deployments → Redeploy the latest deployment');
  console.error('  6. Wait for deployment to complete');
}

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
  const url = apiUrl('/api/signup');
  
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:75',message:'signup function entry',data:{url:url,apiBaseUrl:API_BASE_URL,email:data.email,topicsCount:data.topics.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
  // #endregion
  
  // Always log the URL being used (not sensitive)
  console.log('[Battery Scout] Signup request URL:', url);
  console.log('[Battery Scout] API Base URL:', API_BASE_URL);
  
  try {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:83',message:'Before fetch request',data:{url:url,method:'POST'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    
    console.log('[Battery Scout] Making request to:', url);
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:91',message:'After fetch response received',data:{status:response.status,statusText:response.statusText,ok:response.ok,url:response.url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    
    console.log('[Battery Scout] Response status:', response.status, response.statusText);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
      }
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:96',message:'Response not ok - error data',data:{status:response.status,errorData:errorData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      // Log errors in development only
      if (import.meta.env.DEV) {
        console.error('Signup error:', errorData);
      }
      
      // Handle 404 specifically
      if (response.status === 404) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:105',message:'404 error detected',data:{url:url,apiBaseUrl:API_BASE_URL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        console.error('[Battery Scout] ❌ 404 Error Details:');
        console.error('   Attempted URL:', url);
        console.error('   Response URL:', response.url);
        console.error('   API Base URL:', API_BASE_URL);
        console.error('   Has VITE_API_URL env var:', !!import.meta.env.VITE_API_URL);
        console.error('   VITE_API_URL value:', import.meta.env.VITE_API_URL || 'NOT SET');
        console.error('   Expected endpoint: https://battery-scout-production.up.railway.app/api/signup');
        
        if (API_BASE_URL.includes('localhost')) {
          throw new Error('API endpoint not found. VITE_API_URL is not set in Vercel, or you need to redeploy. Set VITE_API_URL to https://battery-scout-production.up.railway.app and redeploy.');
        }
        
        // Check if URL looks correct
        const expectedUrl = 'https://battery-scout-production.up.railway.app/api/signup';
        if (url !== expectedUrl) {
          console.error(`[Battery Scout] URL mismatch! Expected: ${expectedUrl}, Got: ${url}`);
        }
        
        throw new Error(`API endpoint not found at ${url}. If you just set VITE_API_URL, you MUST redeploy for it to take effect.`);
      }
      
      throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    // Only log success in development
    if (import.meta.env.DEV) {
      console.log('Signup success');
    }
    return result;
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:118',message:'Fetch catch block - error occurred',data:{errorType:error instanceof Error?error.constructor.name:'unknown',errorMessage:error instanceof Error?error.message:String(error),isTypeError:error instanceof TypeError,url:url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    
    console.error('Signup fetch error:', error);
    
    // Network errors (CORS, connection refused, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e892b5bc-800d-41b1-8a74-ae29aec20ff3',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:122',message:'Network error detected',data:{apiBaseUrl:API_BASE_URL,url:url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      console.error('[Battery Scout] ❌ Network Error:');
      console.error('   Error:', error.message);
      console.error('   Attempted URL:', url);
      console.error('   API Base URL:', API_BASE_URL);
      
      if (API_BASE_URL.includes('localhost')) {
        throw new Error(`Cannot connect to backend. VITE_API_URL is not set (using localhost). Set it to https://battery-scout-production.up.railway.app in Vercel and redeploy.`);
      }
      throw new Error(`Cannot connect to backend API at ${API_BASE_URL}. This might be a CORS issue - check that FRONTEND_URL is set in Railway to your Vercel domain.`);
    }
    
    throw error;
  }
}

/**
 * Verify unsubscribe token
 */
export async function verifyUnsubscribeToken(
  token: string
): Promise<UnsubscribeVerifyResponse> {
  const response = await fetch(apiUrl('/api/unsubscribe/verify'), {
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
  const response = await fetch(apiUrl('/api/unsubscribe/confirm'), {
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
  const response = await fetch(apiUrl('/api/topics'));

  if (!response.ok) {
    throw new Error('Failed to fetch topics');
  }

  return response.json();
}

/**
 * Get sample content for preview
 */
export async function getSampleContent(): Promise<ContentResponse> {
  const response = await fetch(apiUrl('/api/content'));

  if (!response.ok) {
    throw new Error('Failed to fetch content');
  }

  return response.json();
}

/**
 * Get subscriber statistics
 */
export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(apiUrl('/api/stats'));

  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }

  return response.json();
}
