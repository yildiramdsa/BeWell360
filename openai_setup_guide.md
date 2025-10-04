# OpenAI API Setup Guide

## Overview
Your BeWell360 app now uses **OpenAI's GPT-3.5-turbo** to provide intelligent, personalized insights and recommendations based on your wellness data.

## Setup Instructions

### 1. Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Click "Create new secret key"
5. Copy the API key (starts with `sk-`)

### 2. Add API Key to Streamlit Secrets
Add your OpenAI API key to your Streamlit secrets:

**For local development:**
Create/edit `.streamlit/secrets.toml`:
```toml
openai_api_key = "sk-your-actual-api-key-here"
```

**For Streamlit Cloud:**
1. Go to your app settings
2. Click "Secrets"
3. Add:
```toml
openai_api_key = "sk-your-actual-api-key-here"
```

### 3. Install Required Package
Add to your `requirements.txt`:
```
openai>=1.0.0
```

### 4. Test the Integration
Run your app and check if AI insights appear. You should see:
- 🤖 AI Insights & Recommendations section
- Personalized messages based on your data
- Actionable recommendations

## What the AI Does

### Sleep Analysis
- Analyzes sleep patterns and duration
- Provides sleep quality recommendations
- Suggests bedtime routines

### Nutrition Analysis
- Reviews meal patterns and hydration
- Suggests dietary improvements
- Provides hydration reminders

### Fitness Analysis
- Evaluates exercise consistency
- Recommends workout improvements
- Motivates when inactive

### Growth Analysis
- Analyzes mood patterns
- Reviews gratitude practice
- Provides encouragement

### Body Composition Analysis
- Tracks weight trends
- Suggests progress strategies
- Provides motivation

## API Costs

**OpenAI GPT-3.5-turbo pricing:**
- Input: $0.0015 per 1K tokens
- Output: $0.002 per 1K tokens

**Estimated cost per user per day:**
- ~$0.001-0.005 (very affordable)
- Monthly cost for 100 users: ~$3-15

## Features

### Smart Data Analysis
- Converts your data into natural language
- Identifies patterns and trends
- Provides context-aware insights

### Personalized Recommendations
- Tailored to your specific data
- Actionable and practical
- Encouraging and motivating

### Beautiful Display
- Color-coded insights (success, warning, info, motivation)
- Clean, modern design
- Easy to read and understand

### Caching
- Insights cached daily to reduce API calls
- Faster loading on subsequent visits
- Cost optimization

## Error Handling

The AI gracefully handles:
- **API failures**: Shows fallback message
- **Rate limits**: Caches responses
- **Invalid data**: Provides helpful error messages
- **Network issues**: Degrades gracefully

## Security & Privacy

### Data Privacy
- Only summary data sent to OpenAI
- No personal identifiers included
- Data used only for analysis

### API Security
- API key stored securely in secrets
- No hardcoded keys in code
- Follows OpenAI security best practices

## Troubleshooting

### Common Issues

**"AI Analysis Error"**
- Check API key is correct
- Verify OpenAI account has credits
- Check internet connection

**"AI Unavailable"**
- API key might be invalid
- OpenAI service might be down
- Check API key permissions

**No insights appearing**
- Ensure data exists in the page
- Check API key configuration
- Verify secrets.toml setup

### Debug Mode
Add this to see API responses:
```python
# In ai_assistant_api.py, add:
import streamlit as st
st.write("Debug - API Response:", response.choices[0].message.content)
```

## Advanced Configuration

### Custom Prompts
Modify the AI prompts in `ai_assistant_api.py`:
```python
def _create_ai_prompt(self, page_type, data_summary):
    # Customize the prompt here
    base_prompt = f"""
    Your custom prompt here...
    """
    return base_prompt
```

### Different Models
Change the model in `generate_insights()`:
```python
response = self.client.chat.completions.create(
    model="gpt-4",  # Use GPT-4 for better quality
    # ... rest of parameters
)
```

### Custom Temperature
Adjust creativity:
```python
temperature=0.3,  # More focused (0.1-0.3)
temperature=0.7,  # Balanced (0.5-0.7)
temperature=1.0,  # More creative (0.8-1.0)
```

## Benefits of API-Based AI

✅ **Intelligent Analysis**: Advanced pattern recognition
✅ **Natural Language**: Conversational, human-like insights
✅ **Personalized**: Tailored to your specific data
✅ **Actionable**: Specific recommendations you can follow
✅ **Scalable**: Handles complex data patterns
✅ **Evolving**: Gets better with OpenAI updates

## Support

For issues with:
- **OpenAI API**: Check [OpenAI Documentation](https://platform.openai.com/docs)
- **Streamlit**: Check [Streamlit Documentation](https://docs.streamlit.io)
- **This Integration**: Review the code in `ai_assistant_api.py`

---

**Your BeWell360 app now has real AI intelligence!** 🚀🤖
