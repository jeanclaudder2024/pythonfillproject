# OpenAI API Setup Guide

## How to Add Your OpenAI API Key

### Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in to your account (or create one if you don't have it)
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the generated API key (it starts with `sk-`)

### Step 2: Add API Key to Your System

**Option A: Edit the .env file (Recommended)**

1. Open the `.env` file in your project folder
2. Replace `your_openai_api_key_here` with your actual API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
FLASK_SECRET_KEY=your-secret-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
```

**Option B: Set Environment Variable**

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Windows Command Prompt:
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Install New Dependencies

Run this command to install OpenAI and dotenv packages:

```bash
pip install openai python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 4: Restart the Application

1. Stop the current Flask app (Ctrl+C)
2. Start it again:
```bash
python app.py
```

## How It Works

### With OpenAI API:
- **Intelligent Data Generation**: Uses GPT to create realistic, contextual vessel data
- **Better Accuracy**: AI understands maritime context and generates appropriate data
- **Consistent Data**: All generated data is coherent and realistic
- **Custom Prompts**: Tailored prompts for maritime industry specifics

### Without OpenAI API:
- **Fallback Mode**: Uses Faker library for random data generation
- **Basic Data**: Simple random data that may not be contextually accurate
- **Still Functional**: System works but with less intelligent data

## Configuration Options

You can customize the OpenAI integration in the `.env` file:

```env
# Model Selection
OPENAI_MODEL=gpt-3.5-turbo          # Faster, cheaper
# OPENAI_MODEL=gpt-4                # More accurate, more expensive

# Token Limits
OPENAI_MAX_TOKENS=1000              # Adjust based on your needs

# API Key
OPENAI_API_KEY=sk-your-key-here     # Your actual API key
```

## Supported Models

- **gpt-3.5-turbo** (Recommended): Fast, cost-effective, good quality
- **gpt-4**: Higher quality but more expensive
- **gpt-4-turbo**: Latest model with better performance

## Cost Considerations

- **GPT-3.5-turbo**: ~$0.001 per 1K tokens
- **GPT-4**: ~$0.03 per 1K tokens
- Each document processing typically uses 500-1000 tokens

## Troubleshooting

### "OpenAI API key not found" Message
- Check that your `.env` file has the correct API key
- Ensure the key starts with `sk-`
- Restart the application after adding the key

### API Errors
- Verify your OpenAI account has available credits
- Check that your API key is valid and not expired
- Ensure you have access to the selected model

### Fallback Mode
- If OpenAI fails, the system automatically uses Faker for data generation
- No manual intervention required
- Check console logs for error details

## Security Notes

- **Never commit your API key to version control**
- The `.env` file should be added to `.gitignore`
- Keep your API key secure and don't share it
- Rotate your API key regularly for security

## Example Generated Data

With OpenAI API, you'll get realistic data like:

```json
{
  "vessel_name": "Pacific Navigator",
  "vessel_type": "Container Ship",
  "flag": "Panama",
  "captain": "Captain James Morrison",
  "company": "Global Maritime Solutions Ltd",
  "port": "Singapore",
  "length": "347 meters",
  "tonnage": "145,000 DWT"
}
```

Without OpenAI, you get basic random data that may not be contextually accurate.