import json
import random
from datetime import date, datetime, timedelta
import streamlit as st
import pandas as pd

class AIAssistant:
    def __init__(self):
        self.insights_cache = {}
    
    def generate_insights(self, page_type, user_data, recent_data=None):
        """Generate rule-based insights for the given page type and data."""
        cache_key = f"{page_type}_{date.today().strftime('%Y-%m-%d')}"
        if cache_key in self.insights_cache:
            return self.insights_cache[cache_key]
        insights = []
        if page_type == "sleep":
            insights.extend(self._sleep_insights(user_data, recent_data))
        elif page_type == "nutrition":
            insights.extend(self._nutrition_insights(user_data, recent_data))
        elif page_type == "fitness":
            insights.extend(self._fitness_insights(user_data, recent_data))
        insights.append(self._get_motivational_message())
        self.insights_cache[cache_key] = insights
        return insights
    
    def _sleep_insights(self, data, recent_data):
        insights = []
        if not data.empty and 'sleep_start' in data.columns and 'sleep_end' in data.columns:
            recent_data = data.tail(7) if len(data) >= 7 else data
            durations = []
            for _, row in recent_data.iterrows():
                try:
                    start_time = pd.to_datetime(row['sleep_start'], format='%H:%M').time()
                    end_time = pd.to_datetime(row['sleep_end'], format='%H:%M').time()
                    start_dt = datetime.combine(date.today(), start_time)
                    end_dt = datetime.combine(date.today(), end_time)
                    
                    if end_dt <= start_dt:
                        end_dt += timedelta(days=1)
                    
                    duration = (end_dt - start_dt).total_seconds() / 3600
                    durations.append(duration)
                except (ValueError, TypeError, KeyError):
                    continue
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                
                if avg_duration < 7:
                    insights.append({
                        "type": "warning",
                        "icon": "⚠️",
                        "title": "Sleep Duration Alert",
                        "message": f"Your average sleep duration is {avg_duration:.1f} hours. Consider aiming for 7-9 hours for optimal health."
                    })
                elif avg_duration > 9:
                    insights.append({
                        "type": "info",
                        "icon": "ℹ️",
                        "title": "Sleep Duration Notice",
                        "message": f"Your average sleep duration is {avg_duration:.1f} hours. While longer sleep can be beneficial, ensure it's quality sleep."
                    })
                else:
                    insights.append({
                        "type": "success",
                        "icon": "✅",
                        "title": "Great Sleep Habits!",
                        "message": f"Your average sleep duration of {avg_duration:.1f} hours is within the recommended range!"
                    })
        
        return insights
    
    def _nutrition_insights(self, data, recent_data):
        insights = []
        
        if not data.empty and 'water_ml' in data.columns:
            recent_data = data.tail(7) if len(data) >= 7 else data
            
            avg_water = recent_data['water_ml'].fillna(0).astype(float).mean()
            
            if avg_water < 2000:
                insights.append({
                    "type": "warning",
                    "icon": "💧",
                    "title": "Hydration Reminder",
                    "message": f"Your average water intake is {avg_water:.0f}ml. Aim for 2-3 liters daily for optimal hydration."
                })
            else:
                insights.append({
                    "type": "success",
                    "icon": "💧",
                    "title": "Excellent Hydration!",
                    "message": f"Great job maintaining {avg_water:.0f}ml average water intake!"
                })
        
        return insights
    
    def _fitness_insights(self, data, recent_data):
        insights = []
        
        if not data.empty:
            recent_data = data.tail(7) if len(data) >= 7 else data
            
            # Check for consistency
            if len(recent_data) >= 3:
                insights.append({
                    "type": "success",
                    "icon": "💪",
                    "title": "Consistency Wins!",
                    "message": f"You've logged {len(recent_data)} activities recently. Keep up the momentum!"
                })
            elif len(recent_data) == 0:
                insights.append({
                    "type": "motivation",
                    "icon": "🏃‍♀️",
                    "title": "Ready to Move?",
                    "message": "Every journey begins with a single step. Log your first activity today!"
                })
        
        return insights
    
    def _get_motivational_message(self):
        messages = [
            "🌟 Every small step counts towards your bigger goals!",
            "💪 Consistency is the key to success. Keep going!",
            "🎯 Progress, not perfection. You're doing great!",
            "⭐ Your dedication to self-improvement is inspiring!",
            "🚀 Small daily improvements lead to big results!",
            "🌈 Every day is a new opportunity to be better!",
            "🔥 You're building habits that will serve you for life!",
            "✨ Your commitment to wellness is your superpower!"
        ]
        return {
            "type": "motivation",
            "icon": random.choice(["🌟", "💪", "🎯", "⭐", "🚀", "🌈", "🔥", "✨"]),
            "title": "Daily Motivation",
            "message": random.choice(messages)
        }
    
    def display_insights(self, insights):
        """Render insight cards in the UI."""
        if not insights:
            return
        st.markdown("### 🤖 AI insights & recommendations")
        for insight in insights:
            icon = insight.get("icon", "💡")
            title = insight.get("title", "Insight")
            message = insight.get("message", "")
            insight_type = insight.get("type", "info")
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
        """Return up to 2 static suggestions for the given page type."""
        suggestions = []
        
        if page_type == "sleep":
            suggestions.extend([
                "💤 Try going to bed 15 minutes earlier tonight",
                "📱 Avoid screens 1 hour before bedtime",
                "🌙 Create a relaxing bedtime routine"
            ])
        elif page_type == "nutrition":
            suggestions.extend([
                "🥗 Add more vegetables to your next meal",
                "💧 Drink a glass of water right now",
                "🍎 Have a piece of fruit as a healthy snack"
            ])
        elif page_type == "fitness":
            suggestions.extend([
                "🚶‍♀️ Take a 10-minute walk",
                "🏃‍♀️ Try a quick 5-minute workout",
                "🧘‍♀️ Do some stretching exercises"
            ])
        
        return suggestions[:2]

ai_assistant = AIAssistant()
