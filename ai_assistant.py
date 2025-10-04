import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import json

class AIAssistant:
    def __init__(self):
        self.insights_cache = {}
    
    def generate_insights(self, page_type, user_data, recent_data=None):
        """Generate AI insights based on page type and user data"""
        
        # Check cache first
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
        elif page_type == "growth":
            insights.extend(self._growth_insights(user_data, recent_data))
        elif page_type == "body_composition":
            insights.extend(self._body_comp_insights(user_data, recent_data))
        
        # Add general motivational message
        insights.append(self._get_motivational_message())
        
        # Cache the insights
        self.insights_cache[cache_key] = insights
        return insights
    
    def _sleep_insights(self, data, recent_data):
        insights = []
        
        if not data.empty and 'sleep_start' in data.columns and 'sleep_end' in data.columns:
            # Calculate average sleep duration
            recent_data = data.tail(7) if len(data) >= 7 else data
            
            durations = []
            for _, row in recent_data.iterrows():
                try:
                    start_time = pd.to_datetime(row['sleep_start'], format='%H:%M').time()
                    end_time = pd.to_datetime(row['sleep_end'], format='%H:%M').time()
                    
                    # Handle overnight sleep
                    start_dt = datetime.combine(date.today(), start_time)
                    end_dt = datetime.combine(date.today(), end_time)
                    
                    if end_dt <= start_dt:
                        end_dt += timedelta(days=1)
                    
                    duration = (end_dt - start_dt).total_seconds() / 3600
                    durations.append(duration)
                except:
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
    
    def _growth_insights(self, data, recent_data):
        insights = []
        
        if not data.empty:
            recent_data = data.tail(7) if len(data) >= 7 else data
            
            # Check mood patterns if available
            if 'mood' in recent_data.columns:
                moods = recent_data['mood'].dropna()
                if len(moods) >= 3:
                    positive_moods = moods[moods.isin(['😀', '😄', '😊', '😍', '🥰', '🙂'])].count()
                    if positive_moods / len(moods) > 0.7:
                        insights.append({
                            "type": "success",
                            "icon": "😊",
                            "title": "Positive Vibes!",
                            "message": "You've been in a great mood lately! Keep nurturing that positivity."
                        })
            
            # Check gratitude practice
            if 'gratitude' in recent_data.columns:
                gratitude_entries = recent_data['gratitude'].dropna()
                if len(gratitude_entries) >= 5:
                    insights.append({
                        "type": "success",
                        "icon": "🙏",
                        "title": "Gratitude Practice",
                        "message": f"Excellent! You've practiced gratitude {len(gratitude_entries)} times recently."
                    })
        
        return insights
    
    def _body_comp_insights(self, data, recent_data):
        insights = []
        
        if not data.empty and len(data) >= 2:
            # Look for trends in weight
            if 'weight_lb' in data.columns:
                recent_data = data.tail(5)
                weights = recent_data['weight_lb'].dropna().astype(float)
                
                if len(weights) >= 2:
                    trend = weights.iloc[-1] - weights.iloc[0]
                    if abs(trend) > 0:
                        direction = "increased" if trend > 0 else "decreased"
                        insights.append({
                            "type": "info",
                            "icon": "📊",
                            "title": "Progress Tracking",
                            "message": f"Your weight has {direction} by {abs(trend):.1f} lbs over the last {len(weights)} entries."
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
        
        import random
        return {
            "type": "motivation",
            "icon": random.choice(["🌟", "💪", "🎯", "⭐", "🚀", "🌈", "🔥", "✨"]),
            "title": "Daily Motivation",
            "message": random.choice(messages)
        }
    
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
        """Generate smart suggestions based on current data"""
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
        
        return suggestions[:2]  # Return top 2 suggestions

# Global AI Assistant instance
ai_assistant = AIAssistant()
