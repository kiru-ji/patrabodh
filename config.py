"""PatraBodh Configuration Module."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
SAMPLES_DIR = BASE_DIR / "samples"

# Inference configuration
INFERENCE_MODE = os.getenv("INFERENCE_MODE", "gemini")  # "gemini" or "ollama"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-12b-it")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Vision configuration
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "560"))

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

# Supported image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Prompt templates for document analysis
SYSTEM_PROMPT = """You are PatraBodh (पत्रबोध), an AI assistant that helps Indian citizens understand government documents.

Your capabilities:
- Read Hindi, English, and bilingual (Hinglish) government forms and notices
- Extract structured information (fields, deadlines, fees, required documents)
- Explain bureaucratic language in simple, plain terms
- Provide actionable next steps

Always respond in the same language as the document. If the document is in Hindi, explain in Hindi. If bilingual, provide both.

Be empathetic and patient. Many users may be first-time readers of government documents."""

DOCUMENT_ANALYSIS_PROMPT = """Analyze this government document image carefully.

Provide your response in the following structured format:

## 📄 Document Type
Identify what type of government document this is (e.g., Aadhaar form, ration card application, PM-KISAN registration, etc.)

## 📝 What This Document Is About
Explain in simple, plain language what this form/document is for and why someone would need it.

## 📋 Key Fields Identified
List the main fields/sections visible in the document with their meanings:
- Field Name → What it means in simple terms

## ⚠️ Important Things to Note
- Deadlines, fees, required supporting documents
- Common mistakes people make filling this form
- Any special instructions visible

## ✅ Next Steps
What should the person do after reading/filling this document? Where should they submit it? What happens next?

## 🔗 Related Government Schemes
If applicable, mention any related government schemes or benefits this document connects to.

Use thinking mode to reason through complex bureaucratic language before explaining."""

FIELD_EXTRACTION_PROMPT = """Extract structured data from this government document. Return ONLY valid JSON inside a ```json block.

Schema:
```json
{
  "document_type": "string - type of document",
  "language": "string - primary language (hi/en/mixed)",
  "title": "string - document title/form name",
  "issuing_authority": "string - government body",
  "fields": [
    {"name": "field label", "value": "extracted value or empty", "required": true/false}
  ],
  "deadlines": ["list of dates/deadlines mentioned"],
  "fees": ["any fees mentioned"],
  "required_documents": ["supporting documents needed"],
  "submission_address": "where to submit",
  "contact_info": "phone/email/office details"
}
```"""


def get_model_config():
    """Return model configuration based on inference mode."""
    if INFERENCE_MODE == "ollama":
        return {
            "mode": "ollama",
            "model": OLLAMA_MODEL,
            "base_url": OLLAMA_BASE_URL,
        }
    else:
        return {
            "mode": "gemini",
            "model": GEMMA_MODEL,
            "api_key": GEMINI_API_KEY,
        }
