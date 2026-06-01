# 🎓 AI Study Assistant v2

## Quick Start

### 1. Install
```
pip install streamlit groq==0.4.2 PyMuPDF python-docx plotly pandas Pillow python-dotenv
```

### 2. Add your Groq API key
Open `.env` and replace:
```
GROQ_API_KEY=your_groq_api_key_here
```
Or paste it directly in **Settings** inside the app.

Get a free key at: https://console.groq.com

### 3. Run
```
streamlit run app.py
```

Open http://localhost:8501

---

## Files
- `app.py` — main app (all 9 pages)
- `database.py` — SQLite storage
- `ai_functions.py` — all Groq AI calls
- `groq_client.py` — Groq client (version-safe)
- `file_reader.py` — PDF/DOCX text extraction
- `uploads/` — your uploaded files
- `study.db` — local database (auto-created)

## What's fixed in v2
- Duplicate upload bug fixed
- Upload box wider and less cramped
- Chat works correctly
- Quiz: all questions shown at once, submit at end, full review with correct/wrong highlighting
- Flashcards: flip to see answer, Right/Wrong buttons with session score
- Summaries: no blank box error
- Progress: 100% real data from your activity, no random numbers
- Settings: clean, no confusing options
- Groq client fixed for all versions (no more 'proxies' error)
