# Vercel Deployment Guide - Battery Scout Frontend

## 🎯 Backend URL
```
https://battery-scout-production.up.railway.app
```

## 📋 Step-by-Step Vercel Setup

### Step 1: Update Git Repository

1. Go to: **https://vercel.com/dashboard**
2. Click on your project: **battery-scout-launchpad**
3. Click **"Settings"** tab
4. Click **"Git"** in left sidebar
5. Under "Connected Git Repository":
   - Click **"Disconnect"** (if there's a Lovable repo connected)
   - Click **"Connect Git Repository"**
   - Select: **`Teslin92/Battery-Scout`**
   - Click **"Connect"**

### Step 2: Set Root Directory

1. Still in **Settings**
2. Click **"General"** in left sidebar
3. Scroll to **"Build & Development Settings"**
4. Find **"Root Directory"** row
5. Click **"Edit"** button
6. Type: `frontend`
7. Click **"Save"**

### Step 3: Configure Build Settings

Still in **Build & Development Settings**, verify/set these:

| Setting | Value |
|---------|-------|
| Framework Preset | `Vite` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

Click **"Save"** if you made any changes.

### Step 4: Set Environment Variable

1. Click **"Environment Variables"** in left sidebar
2. Click **"Add New"** or **"Edit"** if `VITE_API_URL` exists
3. Fill in:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://battery-scout-production.up.railway.app`
   - **Environment**: Select all (Production, Preview, Development)
4. Click **"Save"**

### Step 5: Redeploy

1. Click **"Deployments"** tab at top
2. Find the latest deployment
3. Click the **"..."** menu (three dots)
4. Click **"Redeploy"**
5. Click **"Redeploy"** again to confirm

### Step 6: Wait for Deployment

- Monitor the deployment logs
- Should take 1-2 minutes
- Look for "Build completed" message

---

## 🔧 Update Railway Backend (IMPORTANT!)

After Vercel deploys, get your new Vercel URL and update Railway:

### Your Vercel URL will be something like:
```
https://battery-scout-launchpad.vercel.app
```

### Update Railway:

1. Go to: **https://railway.app/dashboard**
2. Click your **battery-scout-production** project
3. Click **"Variables"** tab
4. Add/Update this variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://battery-scout-launchpad.vercel.app` (your actual Vercel URL)
5. Click **"Add Variable"** or **"Save"**
6. Railway will automatically redeploy

---

## ✅ Verify Everything Works

### Test 1: Frontend Loads
Visit your Vercel URL and check:
- [ ] Page loads without errors
- [ ] Topics/categories load dynamically
- [ ] Sample articles display

### Test 2: API Connection
Open browser console (F12) and check:
- [ ] No CORS errors
- [ ] API calls to Railway backend succeed
- [ ] Network tab shows successful requests to `battery-scout-production.up.railway.app`

### Test 3: Signup Flow
- [ ] Fill out signup form
- [ ] Submit subscription
- [ ] Should see success message
- [ ] Check Supabase to verify subscriber was added

### Test 4: Unsubscribe Flow
- [ ] Check a newsletter email (if you have one)
- [ ] Click unsubscribe link
- [ ] Should redirect to Vercel frontend
- [ ] Confirm unsubscribe works

---

## 🐛 Troubleshooting

### "Failed to fetch" errors
- Check `VITE_API_URL` is set correctly in Vercel
- Verify Railway backend is running (visit the URL directly)

### CORS errors
- Update `FRONTEND_URL` in Railway
- Verify your Vercel URL matches exactly (no trailing slash)

### Topics not loading
- Backend API might not be responding
- Check Railway logs for errors

### Build fails on Vercel
- Verify Root Directory is set to `frontend`
- Check build logs for specific error messages

---

## 📞 Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | https://battery-scout-launchpad.vercel.app | User interface |
| Backend | https://battery-scout-production.up.railway.app | API server |
| API Docs | https://battery-scout-production.up.railway.app/docs | Swagger UI |
| Database | Supabase | Data storage |

---

## 🎉 You're Done!

Once deployed:
1. ✅ Frontend pulls from your Battery-Scout repository
2. ✅ No Lovable dependency
3. ✅ Connected to your Railway backend
4. ✅ Ready for production use

Save this guide for future reference!
