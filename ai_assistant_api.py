import streamlit as st
import pandas as pd
import openai
import json
from datetime import date, datetime
import os

class AIAssistantAPI:
    def __init__(self):
        # Initialize cache, client will be created when needed
        self.client = None
        self.insights_cache = {}
    
    def _get_client(self):
        """Get OpenAI client, creating it if needed"""
        if self.client is None:
            try:
                api_key = st.secrets.get("openai_api_key")
                if not api_key:
                    raise ValueError("OpenAI API key not found in secrets")
                self.client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")
        return self.client
        
    def generate_insights(self, page_type, user_data, recent_data=None):
        """Generate AI insights using OpenAI API"""
        
        # Check cache first
        cache_key = f"{page_type}_{date.today().strftime('%Y-%m-%d')}"
        if cache_key in self.insights_cache:
            return self.insights_cache[cache_key]
        
        try:
            # Prepare data for AI analysis
            data_summary = self._prepare_data_summary(page_type, user_data)
            
            # Create AI prompt
            prompt = self._create_ai_prompt(page_type, data_summary)
            
            # Call OpenAI API
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a wellness coach AI assistant. Provide personalized, actionable insights based on user data. Be encouraging, specific, and helpful. Format responses as JSON with insights array containing type, icon, title, and message fields."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to structured format
            try:
                insights_data = json.loads(ai_content)
                insights = insights_data.get('insights', [])
            except json.JSONDecodeError:
                # Fallback: create structured insight from text response
                insights = [{
                    "type": "info",
                    "icon": "🤖",
                    "title": "AI Insight",
                    "message": ai_content
                }]
            
            # Cache the insights
            self.insights_cache[cache_key] = insights
            return insights
            
        except Exception as e:
            st.error(f"AI Analysis Error: {str(e)}")
            # Return fallback insights
            return [{
                "type": "warning",
                "icon": "⚠️",
                "title": "AI Unavailable",
                "message": "AI insights are temporarily unavailable. Please try again later."
            }]
    
    def _prepare_data_summary(self, page_type, user_data):
        """Prepare data summary for AI analysis"""
        if user_data.empty:
            return f"No {page_type} data available yet."
        
        # Get recent data (last 7 entries)
        recent_data = user_data.tail(7) if len(user_data) >= 7 else user_data
        
        # Create summary based on page type
        if page_type == "sleep":
            return self._summarize_sleep_data(recent_data)
        elif page_type == "nutrition":
            return self._summarize_nutrition_data(recent_data)
        elif page_type == "fitness":
            return self._summarize_fitness_data(recent_data)
        elif page_type == "growth":
            return self._summarize_growth_data(recent_data)
        elif page_type == "body_composition":
            return self._summarize_body_comp_data(recent_data)
        else:
            return f"Recent {page_type} data: {recent_data.to_dict('records')}"
    
    def _summarize_sleep_data(self, data):
        """Summarize sleep data for AI"""
        summary = f"Sleep data for last {len(data)} entries:\n"
        
        for _, row in data.iterrows():
            if 'sleep_start' in row and 'sleep_end' in row:
                summary += f"- Date: {row.get('date', 'Unknown')}, Sleep: {row.get('sleep_start', 'N/A')} to {row.get('sleep_end', 'N/A')}\n"
        
        return summary
    
    def _summarize_nutrition_data(self, data):
        """Summarize nutrition data for AI"""
        summary = f"Nutrition data for last {len(data)} entries:\n"
        
        for _, row in data.iterrows():
            summary += f"- Date: {row.get('date', 'Unknown')}\n"
            if 'water_ml' in row:
                summary += f"  Water: {row.get('water_ml', 0)}ml\n"
            if 'breakfast' in row:
                summary += f"  Breakfast: {row.get('breakfast', 'Not logged')}\n"
            if 'lunch' in row:
                summary += f"  Lunch: {row.get('lunch', 'Not logged')}\n"
            if 'dinner' in row:
                summary += f"  Dinner: {row.get('dinner', 'Not logged')}\n"
        
        return summary
    
    def _summarize_fitness_data(self, data):
        """Summarize fitness data for AI"""
        summary = f"Fitness activities for last {len(data)} entries:\n"
        
        for _, row in data.iterrows():
            summary += f"- Date: {row.get('date', 'Unknown')}\n"
            if 'exercise' in row:
                summary += f"  Exercise: {row.get('exercise', 'N/A')}\n"
            if 'duration_sec' in row:
                duration_min = row.get('duration_sec', 0) / 60
                summary += f"  Duration: {duration_min:.1f} minutes\n"
            if 'distance_km' in row:
                summary += f"  Distance: {row.get('distance_km', 0)}km\n"
        
        return summary
    
    def _summarize_growth_data(self, data):
        """Summarize growth data for AI"""
        summary = f"Growth & reflection data for last {len(data)} entries:\n"
        
        for _, row in data.iterrows():
            summary += f"- Date: {row.get('date', 'Unknown')}\n"
            if 'mood' in row:
                summary += f"  Mood: {row.get('mood', 'N/A')}\n"
            if 'gratitude' in row and pd.notna(row.get('gratitude')):
                gratitude = str(row.get('gratitude', ''))[:100]  # Limit length
                summary += f"  Gratitude: {gratitude}\n"
        
        return summary
    
    def _summarize_body_comp_data(self, data):
        """Summarize body composition data for AI"""
        summary = f"Body composition data for last {len(data)} entries:\n"
        
        for _, row in data.iterrows():
            summary += f"- Date: {row.get('date', 'Unknown')}\n"
            if 'weight_lb' in row:
                summary += f"  Weight: {row.get('weight_lb', 'N/A')} lbs\n"
            if 'body_fat_percent' in row:
                summary += f"  Body Fat: {row.get('body_fat_percent', 'N/A')}%\n"
            if 'skeletal_muscle_percent' in row:
                summary += f"  Muscle: {row.get('skeletal_muscle_percent', 'N/A')}%\n"
        
        return summary
    
    def _create_ai_prompt(self, page_type, data_summary):
        """Create AI prompt based on page type"""
        base_prompt = f"""
Analyze the following {page_type} data and provide 2-3 personalized insights and recommendations:

{data_summary}

Please provide insights in this JSON format:
{{
  "insights": [
    {{
      "type": "success|warning|info|motivation",
      "icon": "appropriate emoji",
      "title": "Brief title",
      "message": "Detailed, actionable message"
    }}
  ]
}}

Focus on:
- Specific patterns you notice
- Actionable recommendations
- Encouraging tone
- Health and wellness best practices
- Progress recognition when appropriate

Be personal, helpful, and motivating. Use appropriate emojis and keep messages concise but informative.
"""
        
        return base_prompt
    
    def display_insights(self, insights):
        """Display insights in a beautiful format"""
        if not insights:
            return
        
        st.markdown("### 🤖 AI Insights & Recommendations")
        
        for insight in insights:
            icon = insight.get("icon", "💡")
            title = insight.get("title", "Insight")
            message = insight.get("message", "")
            insight_type = insight.get("type", "info")
            
            # Choose color based on type
            if insight_type == "success":
                color = "#d4edda"
                border_color = "#c3e6cb"
            elif insight_type == "warning":
                color = "#fff3cd"
                border_color = "#ffeaa7"
            elif insight_type == "motivation":
                color = "#e7f3ff"
                border_color = "#b3d9ff"
            else:  # info
                color = "#d1ecf1"
                border_color = "#bee5eb"
            
            st.markdown(f"""
            <div style="
                background-color: {color};
                border-left: 4px solid {border_color};
                padding: 12px 16px;
                margin: 8px 0;
                border-radius: 4px;
                font-size: 14px;
            ">
                <strong>{icon} {title}</strong><br>
                {message}
            </div>
            """, unsafe_allow_html=True)
    
    def get_smart_suggestions(self, page_type, user_data):
        """Get AI-powered smart suggestions"""
        try:
            data_summary = self._prepare_data_summary(page_type, user_data)
            
            prompt = f"""
Based on this {page_type} data, provide 3 specific, actionable suggestions:

{data_summary}

Return only 3 suggestions, each starting with an emoji and being 1-2 sentences. Be specific and actionable.
"""
            
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a wellness coach. Provide specific, actionable suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip()][:3]
            
        except Exception as e:
            st.error(f"AI Suggestions Error: {str(e)}")
            return ["🤖 AI suggestions temporarily unavailable"]

# Global AI Assistant instance
ai_assistant = AIAssistantAPI()
