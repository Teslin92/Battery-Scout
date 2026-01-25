# Troubleshooting Guide

## "Not Found" Error When Signing Up

If you see a "Not Found" error when trying to sign up, check these:

### 1. Check Vercel Environment Variable

The frontend needs to know where your backend API is located.

**In Vercel Dashboard:**
1. Go to your project → **Settings** → **Environment Variables**
2. Make sure `VITE_API_URL` is set to: `https://battery-scout-production.up.railway.app`
3. Make sure it's enabled for **all environments** (Production, Preview, Development)
4. **Redeploy** after changing environment variables

### 2. Check Browser Console

Open browser DevTools (F12) and check the Console tab when you try to sign up. You should see:
- `API Base URL: https://battery-scout-production.up.railway.app`
- Any error messages with details

### 3. Test Backend Directly

Visit these URLs to verify your backend is working:

- Health check: `https://battery-scout-production.up.railway.app/`
- API docs: `https://battery-scout-production.up.railway.app/docs`
- Topics endpoint: `https://battery-scout-production.up.railway.app/api/topics`

If these don't work, your Railway backend might be down.

### 4. Check CORS Settings

Make sure your Railway backend has `FRONTEND_URL` set to your Vercel domain.

**In Railway:**
1. Go to your project → **Variables**
2. Set `FRONTEND_URL` to your Vercel URL (e.g., `https://battery-scout-launchpad.vercel.app`)
3. Railway will auto-redeploy

### 5. Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "API endpoint not found" | Wrong URL or backend down | Check Railway deployment status |
| "Cannot connect to backend" | Network/CORS issue | Check CORS settings in backend |
| "HTTP 404" | Endpoint doesn't exist | Verify backend is deployed correctly |
| "HTTP 500" | Backend error | Check Railway logs |

### 6. Verify API Endpoint

The signup endpoint should be:
```
POST https://battery-scout-production.up.railway.app/api/signup
```

Test it with curl:
```bash
curl -X POST https://battery-scout-production.up.railway.app/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","topics":["Companies & Deals"],"frequency":"daily"}'
```

---

## Footer Text Not Visible

✅ **Fixed!** The footer now uses proper dark background with light text, matching the Lovable design.

If you still see issues:
- Hard refresh your browser (Cmd+Shift+R / Ctrl+Shift+R)
- Clear browser cache
- Redeploy on Vercel

---

## Still Having Issues?

1. **Check Railway logs** for backend errors
2. **Check Vercel deployment logs** for build errors
3. **Check browser console** for frontend errors
4. **Verify environment variables** are set correctly in both Vercel and Railway
