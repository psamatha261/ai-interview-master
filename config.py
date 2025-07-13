# Configuration file for AI Interview Bot

# Branding Configuration
BRAND_CONFIG = {
    "company_name": "AI Interview Master",
    "logo_url": "https://img.icons8.com/color/96/000000/robot.png",
    "primary_color": "#1f77b4",
    "secondary_color": "#ff7f0e",
    "accent_color": "#2ca02c",
    "theme": "light"  # light, dark, or auto
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    "track_performance": True,
    "save_sessions": True,
    "generate_reports": True,
    "difficulty_weighting": {
        "Easy": 1.0,
        "Medium": 1.5,
        "Hard": 2.0
    }
}

# Voice Configuration
VOICE_CONFIG = {
    "enable_voice": True,
    "voice_language": "en-US",
    "voice_rate": 1.0,
    "voice_volume": 0.8
}

# Interview Configuration
INTERVIEW_CONFIG = {
    "default_questions": 5,
    "max_questions": 15,
    "time_limit_per_question": 300,  # seconds
    "allow_skip": True,
    "show_hints": False
}

# Feedback Configuration
FEEDBACK_CONFIG = {
    "detailed_scoring": True,
    "improvement_suggestions": True,
    "follow_up_questions": True,
    "confidence_analysis": True
} 