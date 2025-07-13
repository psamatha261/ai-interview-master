import streamlit as st
from interview_bot import get_questions_for_session, evaluate_answer, extract_score_from_feedback, get_follow_up_question
from analytics import InterviewAnalytics
from config import BRAND_CONFIG, ANALYTICS_CONFIG, VOICE_CONFIG, INTERVIEW_CONFIG
import json
import random
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

# Initialize analytics
analytics = InterviewAnalytics()

# --- Helper Functions ---
def get_role_avatar(role):
    avatars = {
        "Java Developer": "👨‍💻",
        "AI Engineer": "🤖",
        "Frontend Developer": "🎨",
        "Data Scientist": "📊"
    }
    return avatars.get(role, "🧑‍💼")

def get_difficulty_color(difficulty):
    colors = {
        "Easy": "#28a745",
        "Medium": "#ffc107", 
        "Hard": "#dc3545"
    }
    return colors.get(difficulty, "#6c757d")

def get_difficulty_text_color(difficulty):
    """Get appropriate text color for difficulty badges"""
    if difficulty == "Medium":
        return "#000000"  # Black text for yellow background
    else:
        return "#ffffff"  # White text for other backgrounds

# --- Streamlit Page Config ---
st.set_page_config(
    page_title=BRAND_CONFIG["company_name"],
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS with Branding ---
st.markdown(f"""
<style>
    .main-header {{ 
        font-size: 3rem; 
        font-weight: bold; 
        text-align: center; 
        color: {BRAND_CONFIG["primary_color"]}; 
        margin-bottom: 2rem; 
    }}
    .sub-header {{ 
        font-size: 1.5rem; 
        color: #2c3e50; 
        margin-bottom: 1rem; 
    }}
    .chat-bubble {{ 
        border-radius: 18px; 
        padding: 1rem; 
        margin: 0.5rem 0; 
        max-width: 80%; 
    }}
    .chat-bubble.user {{ 
        background: #e3f2fd; 
        margin-left: auto; 
        text-align: right; 
    }}
    .chat-bubble.bot {{ 
        background: #f0f8ff; 
        margin-right: auto; 
        text-align: left; 
        border-left: 5px solid {BRAND_CONFIG["primary_color"]}; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .avatar {{ 
        font-size: 2rem; 
        vertical-align: middle; 
        margin-right: 0.5rem; 
    }}
    .progress-bar {{ 
        height: 20px; 
        background: #e9ecef; 
        border-radius: 10px; 
        overflow: hidden; 
        margin-bottom: 1rem; 
    }}
    .progress {{ 
        height: 100%; 
        background: {BRAND_CONFIG["primary_color"]}; 
        transition: width 0.3s; 
    }}
    .feedback-box {{ 
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); 
        border-left: 5px solid {BRAND_CONFIG["accent_color"]}; 
        border-radius: 10px; 
        padding: 1rem; 
        margin: 1rem 0; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .difficulty-badge {{
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 2px solid rgba(255,255,255,0.3);
    }}
    .summary-box {{ 
        background: #f1f8e9; 
        border-left: 5px solid {BRAND_CONFIG["accent_color"]}; 
        border-radius: 10px; 
        padding: 1.5rem; 
        margin: 2rem 0; 
    }}
    .stButton > button {{ 
        width: 100%; 
        background: {BRAND_CONFIG["primary_color"]}; 
        color: white; 
        border-radius: 10px; 
        padding: 0.5rem 1rem; 
        font-weight: bold; 
    }}
    .stButton > button:hover {{ 
        background: {BRAND_CONFIG["secondary_color"]}; 
    }}
    .voice-button {{
        background: {BRAND_CONFIG["secondary_color"]} !important;
    }}
    .role-header h3 {{
        margin-bottom: 0.5rem;
    }}
    .role-header .difficulty-badge {{
        margin-left: 1rem;
    }}
    .feedback-box.animated {{
        animation: fadeIn 0.5s ease-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .follow-up {{
        border-left: 5px solid {BRAND_CONFIG["primary_color"]} !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .feature-showcase {{
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .feature-showcase h2 {{
        color: {BRAND_CONFIG["primary_color"]};
        margin-bottom: 1rem;
    }}
    .quick-stats {{
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid {BRAND_CONFIG["accent_color"]};
    }}
    .hint-box {{
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
    }}
    @keyframes slideIn {{
        from {{ transform: translateX(-20px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    .confidence-indicator {{
        background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }}
    .tech-depth-bar {{
        background: linear-gradient(90deg, #4fc3f7 0%, #29b6f6 100%);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'difficulty' not in st.session_state:
    st.session_state['difficulty'] = 'Mixed'
if 'questions' not in st.session_state:
    st.session_state['questions'] = []
if 'answers' not in st.session_state:
    st.session_state['answers'] = []
if 'feedbacks' not in st.session_state:
    st.session_state['feedbacks'] = []
if 'scores' not in st.session_state:
    st.session_state['scores'] = []
if 'current_q' not in st.session_state:
    st.session_state['current_q'] = 0
if 'follow_ups' not in st.session_state:
    st.session_state['follow_ups'] = []
if 'voice_enabled' not in st.session_state:
    st.session_state['voice_enabled'] = VOICE_CONFIG['enable_voice']
if 'interview_style' not in st.session_state:
    st.session_state['interview_style'] = 'Standard'
if 'show_hints' not in st.session_state:
    st.session_state['show_hints'] = True
if 'time_limit' not in st.session_state:
    st.session_state['time_limit'] = False
if 'strict_mode' not in st.session_state:
    st.session_state['strict_mode'] = False

# --- Landing Page ---
def landing_page():
    st.markdown(f'<h1 class="main-header">🤖 {BRAND_CONFIG["company_name"]}</h1>', unsafe_allow_html=True)
    
    # Company branding
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(BRAND_CONFIG["logo_url"], width=100)
    
    # Enhanced feature showcase with animations
    st.markdown("""
    <div class="feature-showcase">
        <h2>🚀 Welcome to the Future of Interview Practice!</h2>
        <p>Experience the most advanced AI-powered interview platform with cutting-edge features:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🎯 **Smart Features**
        - **Role-Specific Questions** with difficulty levels
        - **AI-Powered Evaluation** with 4 different feedback styles
        - **Real-Time Analysis** with confidence tracking
        - **Interactive Hints** for better learning
        """)
    with col2:
        st.markdown("""
        ### 📊 **Advanced Analytics**
        - **Performance Tracking** with detailed metrics
        - **Progress Visualization** with charts and graphs
        - **Session History** for continuous improvement
        - **Downloadable Reports** for portfolio building
        """)
    
    # Quick stats if available
    if ANALYTICS_CONFIG['save_sessions']:
        try:
            history = analytics.get_session_history()
            if history:
                st.markdown("---")
                st.markdown("### 📈 **Your Learning Journey**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Sessions", len(history))
                with col2:
                    avg_score = sum(session.get('average_score', 0) for session in history) / len(history)
                    st.metric("Avg Score", f"{avg_score:.1f}/10")
                with col3:
                    total_questions = sum(session.get('total_questions', 0) for session in history)
                    st.metric("Questions Practiced", total_questions)
                with col4:
                    roles_practiced = len(set(session.get('role', '') for session in history))
                    st.metric("Roles Explored", roles_practiced)
        except:
            pass
    
    st.markdown("---")
    
    with st.form("start_form"):
        with open("question_bank.json") as f:
            question_bank = json.load(f)
        roles = list(question_bank.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Select Job Role:", roles)
            difficulty = st.selectbox("Difficulty Level:", ["Mixed", "Easy", "Medium", "Hard"])
        
        with col2:
            n_questions = st.slider("Number of Questions:", 3, INTERVIEW_CONFIG["max_questions"], INTERVIEW_CONFIG["default_questions"])
            interview_style = st.selectbox("Interview Style:", ["Standard", "Behavioral Focus", "Technical Deep Dive", "System Design", "Quick Fire"])
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                voice_enabled = st.checkbox("Enable Voice Features", value=st.session_state['voice_enabled'])
                show_hints = st.checkbox("Show Hints", value=True)
            with col2:
                time_limit = st.checkbox("Enable Time Limits", value=False)
                strict_mode = st.checkbox("Strict Evaluation", value=False)
        
        submitted = st.form_submit_button("🚀 Start Interview")
        if submitted:
            questions = get_questions_for_session(role, difficulty, n_questions)
            
            if not questions:
                st.error(f"No questions available for {role} with {difficulty} difficulty. Please try a different combination.")
                return
            
            st.session_state['role'] = role
            st.session_state['difficulty'] = difficulty
            st.session_state['interview_style'] = interview_style
            st.session_state['questions'] = questions
            st.session_state['answers'] = [""] * len(questions)
            st.session_state['feedbacks'] = [None] * len(questions)
            st.session_state['scores'] = [None] * len(questions)
            st.session_state['follow_ups'] = [None] * len(questions)
            st.session_state['current_q'] = 0
            st.session_state['voice_enabled'] = voice_enabled
            st.session_state['show_hints'] = show_hints
            st.session_state['time_limit'] = time_limit
            st.session_state['strict_mode'] = strict_mode
            st.session_state['page'] = 'interview'
            st.rerun()

# --- Interview Page ---
def interview_page():
    # Get session state variables with safety checks
    role = st.session_state.get('role', 'Developer')
    difficulty = st.session_state.get('difficulty', 'Medium')
    interview_style = st.session_state.get('interview_style', 'Standard')
    questions = st.session_state.get('questions', [])
    answers = st.session_state.get('answers', [])
    feedbacks = st.session_state.get('feedbacks', [])
    scores = st.session_state.get('scores', [])
    follow_ups = st.session_state.get('follow_ups', [])
    current_q = st.session_state.get('current_q', 0)
    show_hints = st.session_state.get('show_hints', True)
    time_limit = st.session_state.get('time_limit', False)
    strict_mode = st.session_state.get('strict_mode', False)
    
    # Safety checks
    if not questions:
        st.error("No questions available. Please start a new interview session.")
        if st.button("Back to Landing"):
            st.session_state['page'] = 'landing'
            st.rerun()
        return
    
    n_questions = len(questions)
    
    # Ensure current_q is within bounds
    if current_q >= n_questions:
        current_q = n_questions - 1
        st.session_state['current_q'] = current_q
    
    # Ensure all arrays are the right length
    while len(answers) < n_questions:
        answers.append("")
    while len(feedbacks) < n_questions:
        feedbacks.append(None)
    while len(scores) < n_questions:
        scores.append(None)
    while len(follow_ups) < n_questions:
        follow_ups.append(None)
    
    # Update session state
    st.session_state['answers'] = answers
    st.session_state['feedbacks'] = feedbacks
    st.session_state['scores'] = scores
    st.session_state['follow_ups'] = follow_ups
    
    avatar = get_role_avatar(role)
    current_question_data = questions[current_q]

    # Enhanced Progress Bar with Time Tracking
    progress = int((current_q + 1) / n_questions * 100)
    
    # Add time tracking
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = datetime.now()
    
    elapsed_time = datetime.now() - st.session_state['start_time']
    avg_time_per_question = elapsed_time / (current_q + 1) if current_q > 0 else elapsed_time
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<div class="progress-bar"><div class="progress" style="width: {progress}%;"></div></div>', unsafe_allow_html=True)
        st.markdown(f"**Question {current_q + 1} of {n_questions}**")
    with col2:
        st.metric("Progress", f"{progress}%")
    with col3:
        st.metric("Avg Time/Q", f"{avg_time_per_question.seconds//60}m {avg_time_per_question.seconds%60}s")
    
    # Enhanced Role and Difficulty Display
    difficulty_color = get_difficulty_color(current_question_data['difficulty'])
    text_color = get_difficulty_text_color(current_question_data['difficulty'])
    
    # Interview style indicator
    style_colors = {
        "Standard": "#6c757d",
        "Behavioral Focus": "#28a745", 
        "Technical Deep Dive": "#007bff",
        "System Design": "#dc3545",
        "Quick Fire": "#ffc107"
    }
    style_color = style_colors.get(interview_style, "#6c757d")
    
    st.markdown(f"""
    <div class="role-header">
        <h3>{avatar} {role}</h3>
        <span class="difficulty-badge" style="background-color: {difficulty_color}; color: {text_color};">{current_question_data['difficulty']}</span>
        <span class="difficulty-badge" style="background-color: {style_color}; color: white;">{interview_style}</span>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced Chat-style Q&A with Confidence Tracking
    st.markdown(f'<div class="chat-bubble bot"><span class="avatar">{avatar}</span> <b>Interviewer:</b><br>{current_question_data["question"]}</div>', unsafe_allow_html=True)
    
    # Real-time Answer Analysis
    user_answer = st.text_area("Your Answer:", value=answers[current_q], key=f"answer_{current_q}", height=150)
    
    # Real-time feedback indicators
    if user_answer.strip():
        word_count = len(user_answer.split())
        char_count = len(user_answer)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Words", word_count)
        with col2:
            st.metric("Characters", char_count)
        with col3:
            # Confidence indicator based on answer length and content
            confidence = min(10, max(1, word_count // 10 + (1 if any(word in user_answer.lower() for word in ['because', 'example', 'experience', 'implement', 'design', 'approach']) else 0)))
            st.metric("Confidence", f"{confidence}/10")
        with col4:
            # Technical depth indicator
            tech_words = sum(1 for word in ['algorithm', 'optimization', 'architecture', 'design', 'pattern', 'framework', 'api', 'database', 'testing', 'performance'] if word in user_answer.lower())
            st.metric("Tech Depth", f"{tech_words} terms")
    
    st.session_state['answers'][current_q] = user_answer

    # Enhanced Navigation and Evaluation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=current_q==0):
            st.session_state['current_q'] -= 1
            st.rerun()
    
    with col2:
        if st.button("📊 Evaluate Answer"):
            if user_answer.strip():
                with st.spinner("🤖 AI is analyzing your answer..."):
                    feedback = evaluate_answer(current_question_data["question"], user_answer, current_question_data["difficulty"], role)
                    st.session_state['feedbacks'][current_q] = feedback
                    st.session_state['scores'][current_q] = extract_score_from_feedback(feedback)
                    
                    # Generate follow-up question
                    follow_up = get_follow_up_question(current_question_data["question"], user_answer, current_question_data["difficulty"], role)
                    st.session_state['follow_ups'][current_q] = follow_up
                    st.rerun()
            else:
                st.warning("Please provide an answer before evaluation.")
    
    with col3:
        if st.button("Next ➡️", disabled=current_q==n_questions-1):
            st.session_state['current_q'] += 1
            st.rerun()
    
    with col4:
        if st.button("⏭️ Skip", disabled=not INTERVIEW_CONFIG["allow_skip"]):
            st.session_state['current_q'] += 1
            st.rerun()
    
    with col5:
        if show_hints and st.button("💡 Hint"):
            # Show hint based on question type
            hint = get_question_hint(current_question_data["question"], role)
            st.markdown(f'<div class="hint-box">💡 <strong>Hint:</strong> {hint}</div>', unsafe_allow_html=True)

    # Enhanced Feedback Display with Animations
    if feedbacks[current_q]:
        st.markdown(f'<div class="chat-bubble bot"><span class="avatar">{avatar}</span> <b>Interviewer Feedback:</b></div>', unsafe_allow_html=True)
        
        # Animated feedback box
        st.markdown(f'<div class="feedback-box animated">{feedbacks[current_q]}</div>', unsafe_allow_html=True)
        
        # Show follow-up question with enhanced styling
        if follow_ups[current_q]:
            st.markdown(f'<div class="chat-bubble bot follow-up"><span class="avatar">{avatar}</span> <b>Follow-up Question:</b><br>{follow_ups[current_q]}</div>', unsafe_allow_html=True)
    
    # Quick Stats Panel
    if any(s for s in scores if s is not None):
        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        
        answered_count = sum(1 for a in answers if a.strip())
        evaluated_count = sum(1 for s in scores if s is not None)
        avg_score = sum(s for s in scores if s is not None) / evaluated_count if evaluated_count > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Answered", f"{answered_count}/{n_questions}")
        with col2:
            st.metric("Evaluated", f"{evaluated_count}/{n_questions}")
        with col3:
            st.metric("Avg Score", f"{avg_score:.1f}/10")
        with col4:
            best_score = max(s for s in scores if s is not None) if any(s for s in scores if s is not None) else 0
            st.metric("Best Score", f"{best_score}/10")

    # Enhanced End Session Button
    if current_q == n_questions-1 and any(a.strip() for a in answers):
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Finish Interview & See Summary", type="primary", use_container_width=True):
                st.session_state['page'] = 'summary'
                st.rerun()

# Helper function for question hints
def get_question_hint(question, role):
    """Generate helpful hints based on question content and role"""
    question_lower = question.lower()
    
    if 'algorithm' in question_lower or 'complexity' in question_lower:
        return "Think about time and space complexity, and consider different approaches."
    elif 'design' in question_lower or 'architecture' in question_lower:
        return "Consider scalability, maintainability, and trade-offs between different approaches."
    elif 'experience' in question_lower or 'project' in question_lower:
        return "Use the STAR method: Situation, Task, Action, Result."
    elif 'problem' in question_lower or 'challenge' in question_lower:
        return "Break down the problem, explain your approach, and discuss potential solutions."
    elif 'team' in question_lower or 'collaboration' in question_lower:
        return "Focus on communication, conflict resolution, and achieving common goals."
    else:
        return "Provide specific examples and explain your reasoning clearly."

# --- Summary Page ---
def summary_page():
    role = st.session_state['role']
    avatar = get_role_avatar(role)
    questions = st.session_state['questions']
    answers = st.session_state['answers']
    feedbacks = st.session_state['feedbacks']
    scores = st.session_state['scores']
    n_questions = len(questions)

    st.markdown(f'<h1 class="main-header">📊 Interview Summary</h1>', unsafe_allow_html=True)
    
    # Prepare session data for analytics
    session_data = {
        'role': role,
        'difficulty': st.session_state['difficulty'],
        'questions': []
    }
    
    for i, (q_data, a, f, s) in enumerate(zip(questions, answers, feedbacks, scores)):
        session_data['questions'].append({
            'question': q_data['question'],
            'difficulty': q_data['difficulty'],
            'answer': a,
            'feedback': f,
            'score': s
        })
    
    # Generate analytics
    metrics = analytics.generate_performance_metrics(session_data)
    
    if metrics:
        # Save session to analytics
        if ANALYTICS_CONFIG['save_sessions']:
            analytics.save_session(session_data)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Score", f"{metrics['average_score']:.1f}/10")
        with col2:
            st.metric("Weighted Score", f"{metrics['weighted_score']:.1f}/10")
        with col3:
            st.metric("Questions Answered", f"{metrics['answered_questions']}/{metrics['total_questions']}")
        with col4:
            st.metric("Highest Score", f"{metrics['highest_score']}/10")
        
        # Performance charts
        col1, col2 = st.columns(2)
        with col1:
            performance_chart = analytics.create_performance_chart(session_data)
            if performance_chart:
                st.plotly_chart(performance_chart, use_container_width=True)
        
        with col2:
            difficulty_chart = analytics.create_difficulty_chart(session_data)
            if difficulty_chart:
                st.plotly_chart(difficulty_chart, use_container_width=True)
        
        # Strengths and improvements
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths")
            for strength in metrics['strengths']:
                st.markdown(f"✅ {strength}")
        
        with col2:
            st.markdown("### 🎯 Areas for Improvement")
            for improvement in metrics['improvement_areas']:
                st.markdown(f"📝 {improvement}")
    
    # Detailed Q&A review
    st.markdown("---")
    st.markdown("### 📋 Detailed Review")
    
    for i, (q_data, a, f, s) in enumerate(zip(questions, answers, feedbacks, scores)):
        with st.expander(f"Question {i+1}: {q_data['question'][:50]}..."):
            difficulty_color = get_difficulty_color(q_data['difficulty'])
            text_color = get_difficulty_text_color(q_data['difficulty'])
            st.markdown(f"**Difficulty:** <span class='difficulty-badge' style='background-color: {difficulty_color}; color: {text_color};'>{q_data['difficulty']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Your Answer:** {a}")
            if s:
                st.markdown(f"**Score:** {s}/10")
            if f:
                st.markdown(f"**Feedback:** {f}")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Restart Interview"):
            for key in ['page','role','difficulty','questions','answers','feedbacks','scores','current_q','follow_ups']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics"):
            st.session_state['page'] = 'analytics'
            st.rerun()
    
    with col3:
        st.download_button(
            label="📄 Download Report",
            data=json.dumps(session_data, indent=2),
            file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# --- Analytics Page ---
def analytics_page():
    st.markdown(f'<h1 class="main-header">📈 Performance Analytics</h1>', unsafe_allow_html=True)
    
    # Session history
    history = analytics.get_session_history()
    if history:
        st.markdown("### 📊 Recent Sessions")
        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True)
        
        # Performance trends
        if len(history) > 1:
            fig = px.line(df, x='date', y=['avg_score', 'weighted_score'], 
                         title="Performance Trends Over Time")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No previous sessions found. Complete an interview to see analytics!")
    
    if st.button("🏠 Back to Home"):
        st.session_state['page'] = 'landing'
        st.rerun()

# --- Main App Routing ---
if st.session_state['page'] == 'landing':
    landing_page()
elif st.session_state['page'] == 'interview':
    interview_page()
elif st.session_state['page'] == 'summary':
    summary_page()
elif st.session_state['page'] == 'analytics':
    analytics_page() 