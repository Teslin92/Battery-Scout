# Battery Scout - Setup & Security Guide

## 🔐 IMPORTANT: Rotate Your Google Service Account Key

Your current service account key in `credentials.json` has been exposed in your local repository. Follow these steps to create a new, secure key:

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Make sure you're in the **battery-scout** project (check top left dropdown)

### Step 2: Navigate to Service Accounts
1. In the left menu, click **IAM & Admin**
2. Click **Service Accounts**
3. Find the service account: `scout-bot@battery-scout.iam.gserviceaccount.com`

### Step 3: Delete the Old Key
1. Click on the service account email
2. Go to the **KEYS** tab
3. Find the key with ID starting with `8a9aa55e...`
4. Click the three dots (⋮) next to it
5. Click **Delete** and confirm

### Step 4: Create a New Key
1. Still in the KEYS tab, click **ADD KEY**
2. Select **Create new key**
3. Choose **JSON** format
4. Click **Create**
5. A JSON file will download to your computer - **keep this safe!**

### Step 5: Update Your GitHub Secret
1. Go to your GitHub repository: https://github.com/YOUR_USERNAME/Battery-Scout
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Find `GCP_SERVICE_ACCOUNT` in the list
4. Click the **pencil icon** (Update) next to it
5. Open the downloaded JSON file in a text editor
6. Copy the **entire contents** of the file
7. Paste it into the secret value box
8. Click **Update secret**

### Step 6: Delete the Local credentials.json File (IMPORTANT!)
1. On your computer, go to: `/Users/zarko/Documents/Battery Scout/`
2. **Delete** the `credentials.json` file
3. This file is now in `.gitignore` and will never be uploaded to GitHub

---

## 📋 What Was Fixed

### ✅ Security Improvements
- **Removed hardcoded credentials** from `main.py` - now uses environment variables
- **Updated .gitignore** to prevent accidental credential uploads
- **Fixed error handling** in `send_email.py` to provide better debugging

### ✅ Dependencies Fixed
- **Updated requirements.txt** with all missing packages:
  - `google-auth`
  - `google-api-python-client`
  - `google-generativeai`
  - `python-dateutil`
  - `requests`

---

## 🚀 How to Push Changes to GitHub

When you're ready to push these fixes:

1. Open Terminal
2. Navigate to your project:
   ```bash
   cd "/Users/zarko/Documents/Battery Scout"
   ```

3. Check what changed:
   ```bash
   git status
   ```

4. Add the changes:
   ```bash
   git add .gitignore requirements.txt main.py send_email.py
   ```

5. Commit:
   ```bash
   git commit -m "Security fixes: remove hardcoded credentials and update dependencies"
   ```

6. Push to GitHub:
   ```bash
   git push
   ```

---

## 🧪 Test Mode - Safely Test Without Spamming Subscribers

Battery Scout now has a **Test Mode** that lets you test changes without sending emails to all your subscribers!

### How to Enable Test Mode:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TEST_MODE`
5. Value: `true`
6. Click **Add secret**

### (Optional) Set a Custom Test Email:

By default, test emails go to your sender email. To use a different email:

1. Add another secret named `TEST_EMAIL`
2. Value: Your test email address (e.g., `your.test@gmail.com`)
3. Make sure this email exists in your Google Sheet subscribers list!

### Using Test Mode:

**When TEST_MODE is enabled:**
- ✅ Only sends to your test email
- ⏭️  Skips all other subscribers
- 🔍 Shows "TEST MODE ENABLED" in logs

**To run a test:**
1. Make sure `TEST_MODE=true` is set in GitHub Secrets
2. Go to **Actions** tab → **Daily Email Sender**
3. Click **Run workflow** → **Run workflow**
4. Check the logs to see "TEST MODE ENABLED"
5. Only you will receive the email!

**To go back to production:**
1. Go to GitHub Secrets
2. Find `TEST_MODE`
3. Click **Update** and change value to `false`
4. Or simply **delete** the `TEST_MODE` secret

---

## 🔍 Verify Everything Works

After rotating the key and pushing changes:

1. **Enable Test Mode** (see above)
2. Go to your GitHub repository
3. Click **Actions** tab
4. Click **Daily Email Sender** workflow
5. Click **Run workflow** → **Run workflow** (to test manually)
6. Wait a few minutes and check if it succeeds
7. Check your email inbox!

---

## 📧 Questions?

If you see any errors after these changes, check:
- GitHub Actions logs (Actions tab → click the failed run)
- Make sure all GitHub Secrets are set correctly
- Verify the new service account key has permissions for Google Sheets API

---

**Last Updated:** January 6, 2026
