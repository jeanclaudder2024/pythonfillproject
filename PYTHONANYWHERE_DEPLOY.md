# PythonAnywhere Deployment Guide

## Step 1: Upload Files
1. Login to PythonAnywhere
2. Go to Files tab
3. Create folder: utofill
4. Upload all files from your local autofill folder

## Step 2: Install Dependencies
Open Bash console and run:
`ash
cd autofill
pip3.10 install --user -r requirements.txt
`

## Step 3: Create Web App
1. Go to Web tab
2. Add new web app
3. Choose Manual configuration
4. Select Python 3.10

## Step 4: Configure WSGI
1. Edit WSGI configuration file
2. Replace content with wsgi.py content
3. Update 'yourusername' with your actual username

## Step 5: Set Environment Variables
Edit .bashrc file and add:
`ash
export SUPABASE_URL="your_supabase_url_here"
export SUPABASE_ANON_KEY="your_supabase_key_here"
`

## Step 6: Reload and Test
1. Click Reload in Web tab
2. Visit: https://yourusername.pythonanywhere.com
3. Test: https://yourusername.pythonanywhere.com/health

## Your app will be ready!
