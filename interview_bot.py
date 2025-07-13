import random
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Local evaluation system - no OpenAI required
class LocalInterviewEvaluator:
    def __init__(self):
        self.keyword_scores = {
            # Technical keywords with positive scores
            'algorithm': 2, 'optimization': 2, 'efficiency': 2, 'performance': 2,
            'architecture': 2, 'design pattern': 2, 'best practice': 2, 'scalability': 2,
            'testing': 1, 'debug': 1, 'troubleshoot': 1, 'maintenance': 1,
            'documentation': 1, 'code review': 1, 'version control': 1, 'git': 1,
            'database': 1, 'api': 1, 'framework': 1, 'library': 1,
            
            # Java-specific keywords
            'oop': 2, 'inheritance': 2, 'polymorphism': 2, 'encapsulation': 2,
            'interface': 2, 'abstract': 2, 'static': 1, 'final': 1,
            'exception': 1, 'thread': 2, 'concurrency': 2, 'synchronization': 2,
            'garbage collection': 2, 'jvm': 2, 'bytecode': 1, 'spring': 1,
            
            # AI/ML keywords
            'machine learning': 2, 'neural network': 2, 'deep learning': 2,
            'supervised': 1, 'unsupervised': 1, 'regression': 1, 'classification': 1,
            'overfitting': 2, 'cross-validation': 2, 'feature engineering': 2,
            'bias-variance': 2, 'gradient descent': 2, 'optimization': 2,
            'tensorflow': 1, 'pytorch': 1, 'scikit-learn': 1, 'pandas': 1,
            
            # Frontend keywords
            'html': 1, 'css': 1, 'javascript': 1, 'react': 2, 'vue': 1, 'angular': 1,
            'dom': 1, 'responsive': 1, 'accessibility': 1, 'seo': 1,
            'performance': 2, 'optimization': 2, 'browser': 1, 'cross-browser': 1,
            
            # Data Science keywords
            'statistics': 1, 'probability': 1, 'hypothesis': 1, 'p-value': 1,
            'correlation': 1, 'causation': 1, 'outlier': 1, 'missing data': 1,
            'data cleaning': 1, 'exploratory': 1, 'visualization': 1, 'dashboard': 1,
            'a/b testing': 2, 'experiment': 1, 'sample': 1, 'population': 1,
            
            # Negative keywords (reduce score)
            'dont know': -2, 'not sure': -1, 'maybe': -1, 'probably': -1,
            'i think': -1, 'i guess': -1, 'kind of': -1, 'sort of': -1
        }
        
        # Multiple feedback styles for variety
        self.feedback_styles = {
            'encouraging': {
                'excellent': [
                    "🎉 Wow! That was absolutely outstanding! You've clearly mastered this topic.",
                    "🌟 Exceptional work! Your answer demonstrates expert-level understanding.",
                    "💯 Perfect! You've hit all the key points with impressive depth and clarity.",
                    "🚀 Outstanding! This is exactly what interviewers love to hear."
                ],
                'good': [
                    "👍 Great job! You've shown solid understanding of the concepts.",
                    "✅ Well done! Your answer covers the important points effectively.",
                    "👏 Nice work! You're definitely on the right track here.",
                    "💪 Good effort! You've demonstrated solid knowledge in this area."
                ],
                'average': [
                    "🤔 You're getting there! A bit more detail would make this excellent.",
                    "📚 Good start! Let's build on this foundation with more specifics.",
                    "🎯 You're on the right path! Adding examples would strengthen your answer.",
                    "💡 Not bad! With a bit more depth, this could be really strong."
                ],
                'poor': [
                    "💪 Don't worry! Every expert started somewhere. Let's work on this together.",
                    "📖 This is a learning opportunity! The basics are there, just need more practice.",
                    "🌟 Keep going! You've got the right attitude, now let's build the knowledge.",
                    "🎯 You're asking the right questions! Let's dive deeper into this topic."
                ]
            },
            'analytical': {
                'excellent': [
                    "📊 Analysis: Your response demonstrates comprehensive technical knowledge with excellent structure.",
                    "🔍 Evaluation: Outstanding technical depth combined with clear communication patterns.",
                    "📈 Assessment: Expert-level understanding with practical application demonstrated.",
                    "🎯 Review: Exceptional answer showing both theoretical and practical expertise."
                ],
                'good': [
                    "📊 Analysis: Solid technical foundation with good communication structure.",
                    "🔍 Evaluation: Good understanding demonstrated with room for enhancement.",
                    "📈 Assessment: Competent response showing adequate technical knowledge.",
                    "🎯 Review: Well-structured answer with appropriate technical depth."
                ],
                'average': [
                    "📊 Analysis: Basic understanding shown, requires additional technical depth.",
                    "🔍 Evaluation: Adequate response with opportunities for improvement.",
                    "📈 Assessment: Foundational knowledge present, needs expansion.",
                    "🎯 Review: Basic structure good, technical content needs enhancement."
                ],
                'poor': [
                    "📊 Analysis: Limited technical depth, fundamental concepts need review.",
                    "🔍 Evaluation: Basic response structure, technical content requires development.",
                    "📈 Assessment: Minimal technical knowledge demonstrated, needs study.",
                    "🎯 Review: Response lacks technical depth, fundamental understanding needed."
                ]
            },
            'mentor': {
                'excellent': [
                    "👨‍🏫 As your mentor, I'm impressed! You've clearly put in the work to understand this deeply.",
                    "🎓 Excellent work! You've demonstrated the kind of expertise that sets candidates apart.",
                    "💼 From an interviewer's perspective, this answer shows exactly what we look for.",
                    "🏆 Outstanding! You've shown both technical skill and communication ability."
                ],
                'good': [
                    "👨‍🏫 Good work! You're developing strong technical communication skills.",
                    "🎓 Solid foundation! With a bit more practice, you'll be excellent at this.",
                    "💼 You're on the right track! This shows good understanding of the concepts.",
                    "🏆 Well done! You're building the skills needed for technical interviews."
                ],
                'average': [
                    "👨‍🏫 You're making progress! Let's work on adding more technical depth.",
                    "🎓 Good start! The basics are there, now let's add the details that make answers shine.",
                    "💼 You're learning! With more practice, you'll develop stronger technical responses.",
                    "🏆 Keep practicing! You're building the foundation for better answers."
                ],
                'poor': [
                    "👨‍🏫 Let's work on this together! Every expert was once a beginner.",
                    "🎓 Don't get discouraged! This is a learning opportunity to grow your skills.",
                    "💼 We all start somewhere! Let's focus on building your technical knowledge.",
                    "🏆 Keep your head up! With practice and study, you'll improve significantly."
                ]
            },
            'casual': {
                'excellent': [
                    "🔥 That was fire! You totally nailed this question!",
                    "💪 Absolutely crushed it! This is exactly what they want to hear!",
                    "🚀 Boom! You just aced that like a pro!",
                    "🎯 Bullseye! That answer was spot on!"
                ],
                'good': [
                    "👍 Pretty solid! You've got the right idea here.",
                    "✅ Not bad at all! You're definitely getting the hang of this.",
                    "👌 Good stuff! You're on the right track for sure.",
                    "💯 Decent work! You've got the basics down."
                ],
                'average': [
                    "🤔 Hmm, you're close but missing some key details.",
                    "📝 It's a start! Just need to beef it up a bit more.",
                    "🎯 Almost there! Just need to add some more meat to the bones.",
                    "💭 Getting warmer! A few more details would make this really good."
                ],
                'poor': [
                    "😅 Hey, no worries! We all have to start somewhere.",
                    "🤷‍♂️ It happens! Let's work on building this up together.",
                    "💪 Don't sweat it! This is totally learnable stuff.",
                    "🌟 Keep at it! You'll get there with some practice."
                ]
            }
        }
        
        self.follow_up_templates = {
            'Java Developer': [
                "Can you elaborate on how you would implement this in a production environment?",
                "What are the performance implications of this approach?",
                "How would you handle edge cases in this scenario?",
                "Can you explain the trade-offs between different approaches?",
                "What testing strategies would you use for this implementation?"
            ],
            'AI Engineer': [
                "How would you handle data quality issues in this scenario?",
                "What metrics would you use to evaluate this model's performance?",
                "How would you scale this solution for larger datasets?",
                "What are the potential biases in this approach?",
                "How would you deploy this model in production?"
            ],
            'Frontend Developer': [
                "How would you optimize this for mobile devices?",
                "What accessibility considerations should be taken into account?",
                "How would you handle browser compatibility issues?",
                "What performance optimizations would you implement?",
                "How would you structure this for maintainability?"
            ],
            'Data Scientist': [
                "How would you validate these findings?",
                "What additional data sources would you consider?",
                "How would you communicate these results to stakeholders?",
                "What are the limitations of this analysis?",
                "How would you handle missing or inconsistent data?"
            ]
        }

    def evaluate_answer(self, question, answer, difficulty="Medium", role="Developer"):
        """Evaluate answer using local keyword analysis and templates"""
        if not answer or len(answer.strip()) < 10:
            return self._generate_feedback('poor', difficulty, role, 2)
        
        # Calculate base score from keywords
        score = self._calculate_keyword_score(answer.lower())
        
        # Adjust for answer length and structure
        length_bonus = min(len(answer.split()) / 50, 2)  # Bonus for longer answers
        score += length_bonus
        
        # Adjust for difficulty
        if difficulty == "Hard":
            score *= 0.8  # Harder questions get stricter scoring
        elif difficulty == "Easy":
            score *= 1.2  # Easier questions get more lenient scoring
        
        # Normalize score to 1-10 range
        score = max(1, min(10, int(score + 5)))
        
        # Generate feedback based on score
        if score >= 8:
            feedback_type = 'excellent'
        elif score >= 6:
            feedback_type = 'good'
        elif score >= 4:
            feedback_type = 'average'
        else:
            feedback_type = 'poor'
        
        return self._generate_feedback(feedback_type, difficulty, role, score)
    
    def _calculate_keyword_score(self, answer):
        """Calculate score based on keyword presence"""
        score = 0
        for keyword, points in self.keyword_scores.items():
            if keyword in answer:
                score += points
        return score
    
    def _generate_feedback(self, feedback_type, difficulty, role, score):
        """Generate detailed feedback using multiple styles"""
        # Randomly select a feedback style for variety
        style = random.choice(list(self.feedback_styles.keys()))
        main_feedback = random.choice(self.feedback_styles[style][feedback_type])
        
        # Create a comprehensive feedback response
        feedback = f"""
## {main_feedback}

### 📊 **Detailed Breakdown**

**🎯 Question Level:** {difficulty}  
**📈 Your Score:** {score}/10  
**🎨 Feedback Style:** {style.title()}

### 🔍 **Technical Analysis**
{self._get_technical_analysis(score, style)}

### 💬 **Communication Assessment**
{self._get_communication_assessment(score, style)}

### 🎯 **What You Did Well**
{self._get_strengths_detailed(score, style)}

### 🚀 **Areas to Improve**
{self._get_improvements_detailed(score, style)}

### 🤔 **Follow-up Challenge**
{self._get_follow_up(role)}

### 💡 **Pro Tips**
{self._get_pro_tips(score, difficulty, style)}
"""
        return feedback
    
    def _get_technical_analysis(self, score, style):
        if style == 'encouraging':
            if score >= 8:
                return "🌟 Your technical depth is impressive! You showed both theoretical knowledge and practical understanding."
            elif score >= 6:
                return "👍 Good technical foundation! You demonstrated solid understanding of the core concepts."
            elif score >= 4:
                return "📚 You have the basics down! Adding more technical specifics would make this excellent."
            else:
                return "💪 The foundation is there! Focus on building your technical vocabulary and examples."
        elif style == 'analytical':
            if score >= 8:
                return "📊 Technical Depth: Excellent (9/10) - Comprehensive understanding with practical applications."
            elif score >= 6:
                return "📊 Technical Depth: Good (7/10) - Solid understanding with room for enhancement."
            elif score >= 4:
                return "📊 Technical Depth: Basic (5/10) - Adequate knowledge, needs more depth."
            else:
                return "📊 Technical Depth: Limited (3/10) - Fundamental concepts need development."
        elif style == 'mentor':
            if score >= 8:
                return "👨‍🏫 From a technical perspective, you've shown the kind of expertise that interviewers look for."
            elif score >= 6:
                return "👨‍🏫 Your technical understanding is solid. With more practice, you'll be excellent."
            elif score >= 4:
                return "👨‍🏫 You're building good technical foundations. Let's work on adding more depth."
            else:
                return "👨‍🏫 Technical skills develop over time. Focus on understanding the fundamentals first."
        else:  # casual
            if score >= 8:
                return "🔥 Your tech game is strong! You really know your stuff."
            elif score >= 6:
                return "👍 Pretty solid technical knowledge! You've got the right ideas."
            elif score >= 4:
                return "🤔 You're on the right track, just need to beef up the technical details."
            else:
                return "💪 No worries! Technical skills take time to build up."

    def _get_communication_assessment(self, score, style):
        if style == 'encouraging':
            if score >= 8:
                return "🎯 Your communication is crystal clear! You explained complex concepts effectively."
            elif score >= 6:
                return "💬 Good communication flow! Your ideas were well-organized and easy to follow."
            elif score >= 4:
                return "📝 Your communication is improving! Adding structure would make it even better."
            else:
                return "🗣️ Keep practicing your explanations! Clear communication is a skill that develops over time."
        elif style == 'analytical':
            if score >= 8:
                return "📊 Communication: Excellent (9/10) - Clear, structured, and engaging delivery."
            elif score >= 6:
                return "📊 Communication: Good (7/10) - Logical flow with adequate clarity."
            elif score >= 4:
                return "📊 Communication: Basic (5/10) - Understandable but needs better structure."
            else:
                return "📊 Communication: Limited (3/10) - Basic expression, needs clarity improvement."
        elif style == 'mentor':
            if score >= 8:
                return "👨‍🏫 Your communication skills are excellent. You know how to explain technical concepts clearly."
            elif score >= 6:
                return "👨‍🏫 Good communication! You're developing the ability to explain technical topics well."
            elif score >= 4:
                return "👨‍🏫 Communication is improving! Focus on organizing your thoughts before speaking."
            else:
                return "👨‍🏫 Communication skills develop with practice. Don't be afraid to take your time."
        else:  # casual
            if score >= 8:
                return "💯 You explained that like a pro! Crystal clear and easy to follow."
            elif score >= 6:
                return "👍 Nice job explaining! You got your point across well."
            elif score >= 4:
                return "🤔 You're getting better at explaining things! Just need to organize your thoughts more."
            else:
                return "💪 Explaining technical stuff is hard! You'll get better with practice."

    def _get_strengths_detailed(self, score, style):
        if style == 'encouraging':
            if score >= 8:
                return "✅ Deep technical knowledge • Clear communication • Practical examples • Confident delivery"
            elif score >= 6:
                return "✅ Solid understanding • Good communication • Logical thinking • Positive attitude"
            elif score >= 4:
                return "✅ Basic knowledge • Willingness to learn • Honest approach • Good foundation"
            else:
                return "✅ Honest about limitations • Willing to learn • Positive attitude • Good starting point"
        elif style == 'analytical':
            if score >= 8:
                return "📈 Strong technical foundation • Excellent communication skills • Practical application • Professional approach"
            elif score >= 6:
                return "📈 Good technical base • Adequate communication • Logical reasoning • Professional demeanor"
            elif score >= 4:
                return "📈 Basic technical knowledge • Improving communication • Honest assessment • Learning mindset"
            else:
                return "📈 Honest self-assessment • Learning orientation • Positive attitude • Growth potential"
        elif style == 'mentor':
            if score >= 8:
                return "🏆 You've clearly put in the work to understand this deeply. Your technical knowledge is impressive."
            elif score >= 6:
                return "🏆 You're developing strong technical skills. Your communication is getting better with each answer."
            elif score >= 4:
                return "🏆 You have a good foundation to build on. Your honesty about what you know is valuable."
            else:
                return "🏆 Your willingness to learn and improve is your greatest strength. Keep that attitude!"
        else:  # casual
            if score >= 8:
                return "🔥 You totally crushed it! Your tech knowledge and communication are on point."
            elif score >= 6:
                return "👍 You're getting pretty good at this! Solid knowledge and decent communication."
            elif score >= 4:
                return "💪 You've got the basics down! That's a solid foundation to build on."
            else:
                return "🌟 You're honest about what you know, and that's actually really valuable!"

    def _get_improvements_detailed(self, score, style):
        if style == 'encouraging':
            if score >= 8:
                return "🚀 Continue deepening expertise • Stay updated with latest trends • Practice advanced scenarios"
            elif score >= 6:
                return "🚀 Add more specific examples • Practice technical explanations • Study advanced concepts"
            elif score >= 4:
                return "🚀 Study core concepts more thoroughly • Practice explaining technical topics • Add more examples"
            else:
                return "🚀 Focus on fundamental concepts • Practice technical communication • Build confidence gradually"
        elif style == 'analytical':
            if score >= 8:
                return "📊 Continue professional development • Stay current with industry trends • Practice advanced problem-solving"
            elif score >= 6:
                return "📊 Enhance technical depth • Improve communication structure • Practice complex scenarios"
            elif score >= 4:
                return "📊 Strengthen foundational knowledge • Improve communication clarity • Add technical examples"
            else:
                return "📊 Build fundamental understanding • Develop communication skills • Practice basic concepts"
        elif style == 'mentor':
            if score >= 8:
                return "🎓 Keep pushing yourself to learn more advanced topics. You're ready for the next level."
            elif score >= 6:
                return "🎓 Focus on adding more specific examples and technical details to your answers."
            elif score >= 4:
                return "🎓 Spend more time studying the fundamentals and practicing your explanations."
            else:
                return "🎓 Start with the basics and build your confidence. Don't rush the learning process."
        else:  # casual
            if score >= 8:
                return "🔥 Keep leveling up! You're already pretty awesome, but there's always more to learn."
            elif score >= 6:
                return "💪 Add more specific examples and technical details to really nail those answers."
            elif score >= 4:
                return "📚 Hit the books a bit more and practice explaining things out loud."
            else:
                return "🌟 Start with the basics and work your way up. You'll get there!"

    def _get_pro_tips(self, score, difficulty, style):
        tips = []
        
        if difficulty == "Hard":
            tips.append("💡 Hard questions often require multiple approaches - don't be afraid to discuss trade-offs")
        elif difficulty == "Easy":
            tips.append("💡 Easy questions are perfect for showing your communication skills and attention to detail")
        else:
            tips.append("💡 Medium questions are great for demonstrating both knowledge and practical thinking")
        
        if score < 6:
            tips.append("💡 Practice explaining technical concepts to non-technical people")
            tips.append("💡 Use the STAR method: Situation, Task, Action, Result")
        else:
            tips.append("💡 Add specific examples from your experience when possible")
            tips.append("💡 Don't forget to mention trade-offs and considerations")
        
        if style == 'encouraging':
            tips.append("💡 Remember: confidence comes from preparation and practice!")
        elif style == 'analytical':
            tips.append("💡 Structure your answers: Problem → Approach → Solution → Trade-offs")
        elif style == 'mentor':
            tips.append("💡 Interview success is about both knowledge and how you present it")
        else:
            tips.append("💡 Keep it real - interviewers appreciate honesty and authenticity")
        
        return "\n".join(tips)

    def _get_follow_up(self, role):
        if role in self.follow_up_templates:
            return random.choice(self.follow_up_templates[role])
        return "Can you elaborate on that point?"

# Initialize the local evaluator
local_evaluator = LocalInterviewEvaluator()

def get_questions_for_session(role, difficulty="Mixed", n=5):
    """Get questions for a session with specified difficulty level"""
    import json
    with open("question_bank.json") as f:
        question_bank = json.load(f)
    
    if role not in question_bank:
        return []
    
    role_questions = question_bank[role]
    
    if difficulty == "Mixed":
        # Mix questions from all difficulty levels
        all_questions = []
        for diff in ["Easy", "Medium", "Hard"]:
            if diff in role_questions:
                all_questions.extend([(q, diff) for q in role_questions[diff]])
        selected = random.sample(all_questions, min(n, len(all_questions)))
        return [{"question": q, "difficulty": d} for q, d in selected]
    else:
        # Get questions from specific difficulty level
        if difficulty in role_questions:
            questions = random.sample(role_questions[difficulty], min(n, len(role_questions[difficulty])))
            return [{"question": q, "difficulty": difficulty} for q in questions]
        return []

def evaluate_answer(question, answer, difficulty="Medium", role="Developer"):
    """Evaluate the user's answer using local AI (no OpenAI required)"""
    return local_evaluator.evaluate_answer(question, answer, difficulty, role)

def extract_score_from_feedback(feedback):
    """Extract the numerical score from feedback"""
    if not feedback:
        return None
    
    # Look for score patterns like "Score: 8" or "Score: 8/10"
    score_patterns = [
        r'Score:\s*(\d+)',
        r'Score:\s*(\d+)/10',
        r'(\d+)/10',
        r'Score\s*[:：]\s*(\d+)'
    ]
    
    for pattern in score_patterns:
        match = re.search(pattern, feedback, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 1), 10)  # Ensure score is between 1-10
    
    return None

def get_follow_up_question(original_question, user_answer, difficulty="Medium", role="Developer"):
    """Generate a follow-up question based on the user's answer"""
    return local_evaluator._get_follow_up(role) 