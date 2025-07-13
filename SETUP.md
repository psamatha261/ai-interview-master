# 🚀 Quick Setup Guide

## ⚡ Get Started in 3 Steps

### 1. Create Your `.env` File

Create a file named `.env` in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**Get your API key from:** https://platform.openai.com/api-keys

### 2. Run the Application

```bash
streamlit run app.py
```

### 3. Open Your Browser

The app will automatically open at: `http://localhost:8501`

---

## 🎯 How to Use

1. **Select a role** from the sidebar (Java Developer, AI Engineer, etc.)
2. **Click "Start New Interview"** to get a random question
3. **Type your answer** in the text area
4. **Click "Evaluate Answer"** to get AI feedback
5. **Review your score** and improvement suggestions

---

## 🔧 Troubleshooting

**"Error evaluating answer"**
- ✅ Check your OpenAI API key in `.env`
- ✅ Verify internet connection
- ✅ Ensure you have OpenAI API credits

**"Question bank file not found"**
- ✅ Make sure you're in the correct directory
- ✅ Verify `question_bank.json` exists

**Streamlit not starting**
- ✅ Run: `pip install -r requirements.txt`
- ✅ Check Python version (3.7+ required)

---

## 🎉 You're Ready!

Your AI Interview Bot is now running! Practice with different roles and improve your interview skills.

**Happy Interviewing! 🤖** 