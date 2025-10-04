# AI Assistant Integration Guide

## Overview
The AI Assistant provides personalized insights and recommendations for each daily log page. It analyzes user data patterns and provides actionable feedback.

## How to Add AI Assistance to Any Page

### 1. Import the AI Assistant
Add this import at the top of your page:
```python
from ai_assistant import ai_assistant
```

### 2. Add AI Insights Section
Add this code right before your analysis section:
```python
# AI Insights Section
insights = ai_assistant.generate_insights("page_type", st.session_state.your_df)
ai_assistant.display_insights(insights)
```

### 3. Supported Page Types
- `"sleep"` - for sleep schedule analysis
- `"nutrition"` - for nutrition & hydration analysis  
- `"fitness"` - for fitness activities analysis
- `"growth"` - for growth & reflection analysis
- `"body_composition"` - for body composition analysis

### 4. Example Integration

#### For Fitness Activities Page:
```python
# Add import
from ai_assistant import ai_assistant

# Add AI insights section before analysis
insights = ai_assistant.generate_insights("fitness", st.session_state.fitness_df)
ai_assistant.display_insights(insights)
```

#### For Body Composition Page:
```python
# Add import  
from ai_assistant import ai_assistant

# Add AI insights section before analysis
insights = ai_assistant.generate_insights("body_composition", st.session_state.body_comp_df)
ai_assistant.display_insights(insights)
```

## Features

### Smart Insights
- **Sleep Analysis**: Sleep duration tracking, consistency patterns
- **Nutrition Analysis**: Hydration levels, meal patterns
- **Fitness Analysis**: Activity consistency, progress tracking
- **Growth Analysis**: Mood patterns, gratitude practice
- **Body Composition**: Weight trends, progress tracking

### Insight Types
- **Success** (green): Positive patterns and achievements
- **Warning** (yellow): Areas that need attention
- **Info** (blue): Informational insights and trends
- **Motivation** (light blue): Daily motivational messages

### Smart Suggestions
Get contextual suggestions based on current data:
```python
suggestions = ai_assistant.get_smart_suggestions("page_type", user_data)
```

## Customization

### Adding Custom Insights
You can extend the AI assistant by adding new insight types in the `ai_assistant.py` file:

```python
def _custom_insights(self, data, recent_data):
    insights = []
    # Your custom analysis logic here
    return insights
```

### Adding New Page Types
1. Add your page type to the `generate_insights` method
2. Create a corresponding `_your_page_insights` method
3. Add the page type to the integration guide

## Benefits

### For Users:
- **Personalized Feedback**: Get insights tailored to their data
- **Actionable Recommendations**: Clear next steps for improvement
- **Motivation**: Daily encouragement and progress recognition
- **Pattern Recognition**: Understand trends in their wellness journey

### For Developers:
- **Easy Integration**: Just 2 lines of code to add AI assistance
- **Extensible**: Easy to add new insights and page types
- **Cached**: Insights are cached for performance
- **Consistent**: Same AI experience across all pages

## Performance Notes
- Insights are cached daily to avoid repeated calculations
- Analysis is performed on recent data (last 7 entries) for relevance
- Lightweight processing that doesn't slow down page loads
