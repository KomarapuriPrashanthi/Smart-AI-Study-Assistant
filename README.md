# 📚 Smart AI Study Assistant

An AI-powered Study Assistant built using Streamlit and LangChain.

This application helps students:
- Generate quizzes from study material
- Create interactive flashcards
- Generate audio summaries
- Track study progress

---

## 🚀 Features

### 📝 Quiz Generator
- Automatically generates MCQ-based quizzes
- Instant score calculation
- Stores previous attempts

### 🧠 Flashcards
- Interactive card-style flashcards
- Flip to reveal answers
- Navigate between cards

### 🔊 Audio Summary
- Generates AI-powered summary
- Text-to-speech integration

### 📊 Study Progress Dashboard
- Tracks total attempts
- Calculates average score
- Displays previous attempts history

---

## 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- Groq API
- SQLite (for progress tracking)
- dotenv

---

## ⚙️ Installation & Setup

1. Clone the repository:

```
git clone https://github.com/KomarapuriPrashanthi/Smart-AI-Study-Assistant.git
```

2. Navigate to the project folder:

```
cd Smart-AI-Study-Assistant
```

3. Create a virtual environment:

```
python -m venv venv
```

4. Activate virtual environment:

Windows:
```
venv\Scripts\activate
```

5. Install dependencies:

```
pip install -r requirements.txt
```

6. Create a `.env` file and add your Groq API key:

```
GROQ_API_KEY=your_api_key_here
```

7. Run the application:

```
python -m streamlit run app.py
```

---

## 📌 Project Status

✅ Week 1 Completed  
Core features implemented successfully.
