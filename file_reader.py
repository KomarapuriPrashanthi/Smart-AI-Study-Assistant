import os
import fitz
from docx import Document as DocxDocument

def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            doc = fitz.open(filepath)
            text = "".join(p.get_text() for p in doc)
            doc.close()
            return text
        elif ext in [".docx", ".doc"]:
            doc = DocxDocument(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    return ""

def get_page_count(filepath: str) -> int:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            doc = fitz.open(filepath)
            n = doc.page_count
            doc.close()
            return n
    except:
        pass
    return 1
