# Railway Backend Configuration Checklist

## 🔍 Verify Your Backend is Running

Visit: **https://battery-scout-production.up.railway.app**

You should see:
```json
{
  "status": "healthy",
  "service": "Battery Scout API",
  "version": "2.0.0",
  "database": "Supabase"
}
```

If you see this, your backend is working! ✅

## 📋 Required Environment Variables in Railway

Make sure these are ALL set in your Railway project:

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Service role key (secret) | Supabase Dashboard → Settings → API → service_role |
| `GEMINI_API_KEY` | Google AI API key | https://makersuite.google.com/app/apikey |
| `GMAIL_USER` | Your Gmail address | Your email for sending newsletters |
| `GMAIL_APP_PASSWORD` | Gmail app password | Gmail → Security → App passwords |
| `UNSUBSCRIBE_SALT` | Random secret string | Any random string (e.g., `my-secret-salt-123`) |
| `FRONTEND_URL` | Your Vercel frontend URL | `https://battery-scout-launchpad.vercel.app` |
| `PORT` | (Auto-set by Railway) | Leave this, Railway sets it automatically |

## 🔧 How to Check/Add Variables in Railway

1. Go to: https://railway.app/dashboard
2. Click: **battery-scout-production**
3. Click: **Variables** tab
4. Review each variable above
5. If missing, click **"New Variable"** and add it

## ⚠️ Important Notes

### `FRONTEND_URL`
- Must be set to your exact Vercel URL
- **With** `https://`
- **Without** trailing slash
- Example: `https://battery-scout-launchpad.vercel.app`

### `SUPABASE_SERVICE_KEY`
- Use the **service_role** key (not anon key)
- This is different from `VITE_SUPABASE_PUBLISHABLE_KEY` used in frontend

### `GMAIL_APP_PASSWORD`
- **Not** your regular Gmail password
- Must create "App Password" in Google Account settings
- Go to: Google Account → Security → 2-Step Verification → App passwords

## 🧪 Test Your Backend

### Test 1: Health Check
```bash
curl https://battery-scout-production.up.railway.app
```

Should return: `{"status":"healthy",...}`

### Test 2: Topics API
```bash
curl https://battery-scout-production.up.railway.app/api/topics
```

Should return: List of categories

### Test 3: Sample Content
```bash
curl https://battery-scout-production.up.railway.app/api/content
```

Should return: Sample articles

### Test 4: API Documentation
Visit: https://battery-scout-production.up.railway.app/docs

Should show: Swagger UI with all endpoints

## ✅ Backend is Ready When:

- [ ] Health check returns healthy status
- [ ] `/api/topics` returns categories
- [ ] `/api/content` returns articles
- [ ] No errors in Railway logs
- [ ] All environment variables are set

## 🚨 Common Issues

### "502 Bad Gateway"
- Backend crashed or not deployed
- Check Railway logs for errors
- Verify all environment variables are set

### "Database connection failed"
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Verify Supabase project is active

### "Internal Server Error"
- Check Railway logs for specific error
- Likely missing environment variable

## 📊 Check Railway Logs

1. Go to Railway dashboard
2. Click your project
3. Click **"Deployments"** tab
4. Click latest deployment
5. View logs in real-time

Look for:
- `✅ Uvicorn running on...`
- Any error messages in red
- Database connection confirmations
