# 🎓 Smart AI Study Assistant

An AI-powered study companion built using Python, Streamlit, Groq LLM, and SQLite that helps students learn more effectively from their study materials.

The application allows users to upload documents, interact with them through AI-powered conversations, generate quizzes, create flashcards, summarize content, track learning progress, and plan study sessions — all within a single platform.

---

## 🚀 Features

### 📁 Document Management

* Upload and organize study materials
* Support for PDF and DOCX documents
* Store and manage learning resources in one place

### 💬 Chat with PDF

* Ask questions directly from uploaded documents
* Context-aware AI responses
* Instant doubt clarification from study material

### 🧠 AI Quiz Generator

* Automatically generate quizzes from uploaded content
* Multiple-choice questions
* Detailed answer review after submission
* Performance evaluation and scoring

### 🃏 Flashcards

* Generate flashcards from study materials
* Interactive flip-card learning experience
* Right/Wrong tracking system
* Session-based performance monitoring

### 📝 Smart Summaries

* Generate concise study notes
* Extract key concepts and important points
* Quick revision support

### 📅 Study Planner

* Create and manage study plans
* Organize learning schedules
* Improve study consistency

### 📊 Progress Tracking

* Monitor learning activity
* Quiz performance analytics
* Flashcard statistics
* Document usage insights

### 🎨 Modern User Interface

* Clean and intuitive dashboard
* Easy navigation between modules
* Student-friendly design

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### Database

* SQLite

### AI Model

* Groq LLM

### Libraries

* PyMuPDF
* python-docx
* pandas
* plotly
* Pillow
* python-dotenv

---

## 📂 Project Structure

```text
Smart-AI-Study-Assistant
│
├── app.py
├── ai_functions.py
├── database.py
├── file_reader.py
├── groq_client.py
├── requirements.txt
├── README.md
└── .gitignore
```

### File Description

| File             | Purpose                                   |
| ---------------- | ----------------------------------------- |
| app.py           | Main Streamlit application                |
| ai_functions.py  | AI-powered features and Groq interactions |
| database.py      | SQLite database operations                |
| file_reader.py   | PDF and DOCX processing                   |
| groq_client.py   | Groq API configuration                    |
| requirements.txt | Project dependencies                      |

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/KomarapuriPrashanthi/Smart-AI-Study-Assistant.git
cd Smart-AI-Study-Assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=YOUR_API_KEY
```

Get your API key from the Groq Console.

### 4. Run Application

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 🎯 Use Cases

* Students preparing for exams
* Quick revision before tests
* Learning from PDF notes
* Generating practice quizzes
* Building flashcard-based study routines
* Tracking study performance

---

## 🔒 Security

Sensitive files are excluded from GitHub:

* `.env`
* `study.db`
* `uploads/`
* `__pycache__/`

---


## 🎥 Project Demo

Watch the demo video here:

[Demo Video](https://github.com/user-attachments/assets/0c5f8ae4-878a-4040-a20f-876b9503f3f9)







```
```
