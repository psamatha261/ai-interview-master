import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from config import ANALYTICS_CONFIG

class InterviewAnalytics:
    def __init__(self):
        self.sessions_file = "interview_sessions.json"
        self.load_sessions()
    
    def load_sessions(self):
        """Load existing interview sessions from file"""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = []
    
    def save_session(self, session_data):
        """Save a new interview session"""
        session_data['timestamp'] = datetime.now().isoformat()
        session_data['session_id'] = len(self.sessions) + 1
        self.sessions.append(session_data)
        
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def calculate_weighted_score(self, scores, difficulties):
        """Calculate weighted score based on difficulty levels"""
        total_weighted = 0
        total_weight = 0
        
        for score, difficulty in zip(scores, difficulties):
            weight = ANALYTICS_CONFIG['difficulty_weighting'].get(difficulty, 1.0)
            total_weighted += score * weight
            total_weight += weight
        
        return total_weighted / total_weight if total_weight > 0 else 0
    
    def generate_performance_metrics(self, session_data):
        """Generate detailed performance metrics for a session"""
        scores = []
        difficulties = []
        
        for q_data in session_data['questions']:
            if 'score' in q_data and q_data['score']:
                scores.append(q_data['score'])
                difficulties.append(q_data.get('difficulty', 'Medium'))
        
        if not scores:
            return None
        
        metrics = {
            'total_questions': len(session_data['questions']),
            'answered_questions': len(scores),
            'average_score': sum(scores) / len(scores),
            'weighted_score': self.calculate_weighted_score(scores, difficulties),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'score_range': max(scores) - min(scores),
            'difficulty_breakdown': self.get_difficulty_breakdown(difficulties),
            'strengths': self.identify_strengths(session_data),
            'improvement_areas': self.identify_improvements(session_data)
        }
        
        return metrics
    
    def get_difficulty_breakdown(self, difficulties):
        """Get breakdown of questions by difficulty"""
        breakdown = {}
        for diff in difficulties:
            breakdown[diff] = breakdown.get(diff, 0) + 1
        return breakdown
    
    def identify_strengths(self, session_data):
        """Identify areas of strength based on feedback"""
        strengths = []
        for q_data in session_data['questions']:
            if 'score' in q_data and q_data['score'] and q_data['score'] >= 8:
                strengths.append(f"Strong performance on: {q_data['question'][:50]}...")
        return strengths[:3]  # Top 3 strengths
    
    def identify_improvements(self, session_data):
        """Identify areas for improvement based on feedback"""
        improvements = []
        for q_data in session_data['questions']:
            if 'score' in q_data and q_data['score'] and q_data['score'] <= 6:
                improvements.append(f"Needs improvement on: {q_data['question'][:50]}...")
        return improvements[:3]  # Top 3 improvements
    
    def create_performance_chart(self, session_data):
        """Create a performance chart for the session"""
        scores = []
        question_labels = []
        
        for i, q_data in enumerate(session_data['questions']):
            if 'score' in q_data and q_data['score']:
                scores.append(q_data['score'])
                question_labels.append(f"Q{i+1}")
        
        if not scores:
            return None
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=question_labels,
            y=scores,
            mode='lines+markers',
            name='Score',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Interview Performance Over Questions",
            xaxis_title="Question Number",
            yaxis_title="Score (1-10)",
            yaxis=dict(range=[0, 10]),
            height=400
        )
        
        return fig
    
    def create_difficulty_chart(self, session_data):
        """Create a chart showing performance by difficulty"""
        difficulty_scores = {'Easy': [], 'Medium': [], 'Hard': []}
        
        for q_data in session_data['questions']:
            if 'score' in q_data and q_data['score'] and 'difficulty' in q_data:
                difficulty = q_data['difficulty']
                if difficulty in difficulty_scores:
                    difficulty_scores[difficulty].append(q_data['score'])
        
        # Calculate averages
        avg_scores = {}
        for diff, scores in difficulty_scores.items():
            if scores:
                avg_scores[diff] = sum(scores) / len(scores)
        
        if not avg_scores:
            return None
        
        fig = px.bar(
            x=list(avg_scores.keys()),
            y=list(avg_scores.values()),
            title="Average Score by Difficulty Level",
            labels={'x': 'Difficulty', 'y': 'Average Score'},
            color=list(avg_scores.values()),
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=400)
        return fig
    
    def get_session_history(self):
        """Get summary of all interview sessions"""
        if not self.sessions:
            return None
        
        history = []
        for session in self.sessions[-10:]:  # Last 10 sessions
            metrics = self.generate_performance_metrics(session)
            if metrics:
                history.append({
                    'date': session['timestamp'][:10],
                    'role': session['role'],
                    'avg_score': metrics['average_score'],
                    'weighted_score': metrics['weighted_score'],
                    'questions': metrics['total_questions']
                })
        
        return history 