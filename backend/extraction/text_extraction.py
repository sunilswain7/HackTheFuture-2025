import pdfplumber
import docx
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        text = f"[ERROR: Could not read PDF - {str(e)}]"
    return text

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"[ERROR: Could not read DOCX - {str(e)}]"

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[ERROR: Could not read TXT - {str(e)}]"

def extract_text(file_path: str, content_type: str) -> Optional[str]:
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return extract_text_from_docx(file_path)
    elif content_type.startswith("text/"):
        return extract_text_from_txt(file_path)
    else:
        return "[UNSUPPORTED FILE TYPE]"
