import json
import re
from groq_client import chat

# ── helpers ───────────────────────────────────────────────────────────────────
def _trunc(text, n=5500):
    return text[:n] if len(text) > n else text

def _extract_json_array(raw: str) -> list:
    """Try to pull a JSON array out of a raw LLM response."""
    raw = raw.strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON array found in response")

# ── chat with document ────────────────────────────────────────────────────────
def doc_chat(doc_text: str, history: list, user_msg: str) -> str:
    system = f"""You are an AI Study Assistant helping a student understand their study material.
Document content:
--- START ---
{_trunc(doc_text)}
--- END ---
Answer based on the document. Be clear and educational."""
    msgs = [{"role": "system", "content": system}]
    msgs += history[-10:]
    msgs.append({"role": "user", "content": user_msg})
    return chat(msgs, max_tokens=1024)

# ── quiz ──────────────────────────────────────────────────────────────────────
def generate_quiz(doc_text: str, num: int, difficulty: str, qtype: str) -> list:
    prompt = f"""From this document generate exactly {num} {qtype} questions at {difficulty} difficulty.

DOCUMENT:
{_trunc(doc_text)}

Return ONLY a JSON array. Each item:
{{
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "A",
  "explanation": "..."
}}
For True/False use options ["A. True","B. False"] and answer "A" or "B".
Return ONLY the JSON array, nothing else."""
    raw = chat([{"role": "user", "content": prompt}], max_tokens=3000, temperature=0.4)
    return _extract_json_array(raw)

# ── flashcards ────────────────────────────────────────────────────────────────

def generate_flashcards(doc_text: str, num: int) -> list:
    prompt = f"""From this document create exactly {num} flashcard question-answer pairs.

DOCUMENT:
{_trunc(doc_text)}

Return ONLY a valid JSON array, nothing else, no explanation:
[{{"question": "...", "answer": "..."}}]"""
    raw = chat([{"role": "user", "content": prompt}], max_tokens=2500, temperature=0.4)
    return _extract_json_array(raw)

# ── summary ───────────────────────────────────────────────────────────────────
def generate_summary(doc_text: str, doc_name: str) -> str:
    prompt = f"""Write a comprehensive study summary for "{doc_name}".

DOCUMENT:
{_trunc(doc_text)}

Structure:
## Overview
(2-3 sentences)

## Key Topics
- bullet points

## Important Concepts
- definitions and explanations

## Key Takeaways
- most important study points"""
    return chat([{"role": "user", "content": prompt}], max_tokens=1500)
