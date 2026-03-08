# 📚 Smart AI Study Assistant

An AI-powered Study Assistant built using **Streamlit, LangChain, and Groq API**.

This application helps students learn smarter by generating quizzes, flashcards, and audio summaries from **text or uploaded PDF notes**, while also tracking their study progress.

---

# 🚀 Features

### 📝 Quiz Generator

* Automatically generates MCQ-based quizzes from study material
* Instant score calculation
* Stores previous quiz attempts in database

### 🧠 Flashcards

* Interactive card-style flashcards
* Flip cards to reveal answers
* Navigate between multiple cards

### 🔊 Audio Summary

* Generates AI-powered summary of study material
* Converts summary into speech using text-to-speech

### 📄 PDF Upload Support (Week 2)

* Upload PDF study notes
* Extracts text automatically
* Generate quizzes, flashcards, and summaries from the PDF

### 📊 Study Progress Dashboard

* Tracks total quiz attempts
* Calculates average score
* Displays previous attempt history

---

# 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **LangChain**
* **Groq API**
* **SQLite** (for progress tracking)
* **dotenv**
* **pypdf** (for PDF text extraction)
* **gTTS** (for audio generation)

---

# ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/KomarapuriPrashanthi/Smart-AI-Study-Assistant.git
```

### 2️⃣ Navigate to project folder

```
cd Smart-AI-Study-Assistant
```

### 3️⃣ Create virtual environment

```
python -m venv venv
```

### 4️⃣ Activate virtual environment

Windows:

```
venv\Scripts\activate
```

### 5️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 6️⃣ Create `.env` file and add Groq API key

```
GROQ_API_KEY=your_api_key_here
```

### 7️⃣ Run the application

```
python -m streamlit run app.py
```

---

# 📌 Project Status

✅ Week 1 Completed

* Quiz generation
* Flashcards
* Audio summary
* Study progress dashboard

✅ Week 2 Completed

* PDF upload support
* Automatic text extraction from PDFs

---

# 📷 Future Improvements

* Better quiz difficulty levels
* Smarter flashcards
* Study analytics dashboard
* Multi-document support
* Better UI for learning focus