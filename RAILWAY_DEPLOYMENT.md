# Railway Deployment Guide for Autofill Project

## 🚀 Quick Start

### Step 1: Go to Railway
1. Visit [railway.app](https://railway.app)
2. Sign up/login with GitHub

### Step 2: Deploy from GitHub
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `pythonfillproject` repository
4. Railway will auto-detect Python and deploy

### Step 3: Set Environment Variables
In Railway dashboard, add these variables:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_key_here
PORT=8000
```

### Step 4: Get Your URL
1. Railway will provide a URL like: `https://your-app.railway.app`
2. Update your React project with this URL
3. Test: `https://your-app.railway.app/health`

## ✅ Files Created for Railway

- `requirements.txt` - Python dependencies
- `railway.json` - Railway configuration
- `Procfile` - Start command
- `runtime.txt` - Python version
- `working_fastapi.py` - Main FastAPI app

## 📋 Important Notes

1. **Environment Variables**: Don't forget to add Supabase credentials
2. **Start Command**: Railway uses `uvicorn working_fastapi:app --host 0.0.0.0 --port $PORT`
3. **Python Version**: 3.11.0
4. **Auto-Deploy**: Every GitHub push will redeploy

## 🎯 What Railway Supports

- ✅ Full Python support
- ✅ `docx2pdf` package (Windows/Linux)
- ✅ File system access
- ✅ FastAPI/uvicorn
- ✅ Free tier available

## 🔧 Troubleshooting

### If deployment fails:
1. Check Railway logs
2. Verify all environment variables are set
3. Ensure GitHub repo is up to date
4. Check Python version compatibility

### If API doesn't respond:
1. Check Railway logs for errors
2. Test `/health` endpoint
3. Verify environment variables
4. Check CORS settings

## 📱 Next Steps

1. Deploy to Railway
2. Get deployment URL
3. Update React project API_BASE_URL
4. Test template upload and document generation

## 🆘 Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally first
4. Check Supabase connection

