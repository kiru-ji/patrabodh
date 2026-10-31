# PatraBodh 📄🔍
## Multimodal Document Understanding for Rural Government Services

**Built with Gemma 4 | Hacktoberfest Hack Day Noida 2026 | Best Use of Gemma 4 Track**

PatraBodh (पत्रबोध = "document understanding") is an offline-first multimodal AI assistant that helps rural Indian citizens understand government forms, notices, and letters by simply pointing their phone camera at them. It reads Hindi/English/bilingual documents using Gemma 4's vision capabilities and explains them in plain language with actionable next steps.

### 🏆 Why This Project?

- **400M+ Indians** struggle with bureaucratic government documents
- Government forms use complex Hindi/English terminology that rural citizens find confusing
- No existing tool combines **vision + multilingual OCR + plain-language explanation** for Indian government documents
- Runs **offline** on a laptop — no internet needed, preserving privacy and accessibility

### ✨ Key Features

- 📸 **Camera-to-Explanation**: Point camera at any government form → get plain-language explanation
- 🇮🇳 **Bilingual Support**: Handles Hindi, English, and mixed (Hinglish) documents
- 🧠 **Thinking Mode**: Uses Gemma 4's reasoning to break down complex bureaucratic language
- 📋 **Structured Extraction**: Identifies form fields, deadlines, required documents, and fees
- 🔌 **Dual-Mode**: Works via Gemini API (cloud) or Ollama (fully offline)
- 📱 **Mobile-Responsive PWA**: Works on phones, tablets, and laptops
- 🔒 **Privacy-First**: Offline mode means no data leaves the device

### 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Gemma 4 12B (primary) / E4B (edge fallback) |
| Vision Pipeline | HuggingFace Transformers `image-text-to-text` |
| Cloud Inference | Google Gemini API (free tier) |
| Local Inference | Ollama (`gemma4:12b`) |
| Backend | FastAPI (Python 3.11+) |
| Frontend | Vanilla HTML/CSS/JS (PWA-ready) |
| Image Processing | Pillow + OpenCV |
| Token Budget | 560 visual tokens (optimized for OCR) |

### 🚀 Quick Start

```bash
# 1. Clone and install
cd patrabodh
pip install -r requirements.txt

# 2. Set up your Gemini API key (cloud mode)
export GEMINI_API_KEY="your-key-here"

# OR use Ollama for fully offline mode
ollama pull gemma4:12b

# 3. Run the app
python app.py

# 4. Open http://localhost:8000
```

### 📁 Project Structure

```
patrabodh/
├── app.py                  # FastAPI application entry point
├── config.py               # Configuration (model selection, token budget)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── engine/
│   ├── __init__.py
│   ├── vision_pipeline.py  # Gemma 4 vision OCR pipeline
│   ├── explainer.py        # Plain-language explanation generator
│   ├── field_extractor.py  # Structured field extraction
│   └── inference.py        # Dual-mode inference (Gemini API / Ollama)
├── knowledge/
│   ├── __init__.py
│   ├── schemes.json        # Government scheme database
│   └── document_types.json # Known document type templates
├── static/
│   ├── index.html          # Main web UI
│   ├── style.css           # Mobile-responsive styles
│   ├── app.js              # Frontend logic (camera, upload, display)
│   └── manifest.json       # PWA manifest
├── samples/                # Sample government document images
│   └── README.md           # Description of sample documents
├── tests/
│   └── test_engine.py      # Unit tests for core engine
├── Dockerfile              # Container deployment
├── docker-compose.yml      # Docker Compose with Ollama
└── DEPLOY.md               # DigitalOcean deployment guide
```

### 🎯 Demo Script (3-minute presentation)

1. **Show the problem** (30s): Display a complex Hindi government form. Ask audience: "Can you tell what this form requires?"
2. **Live demo** (90s): Upload the form → watch PatraBodh extract fields, explain in plain Hindi, show next steps
3. **Offline mode** (30s): Disconnect WiFi → show it still works via local Ollama
4. **Impact** (30s): "400 million Indians interact with these documents daily. PatraBodh makes government accessible."

### 📊 Judging Criteria Alignment

| Criteria | How PatraBodh Scores |
|----------|---------------------|
| **Multimodal Experience** | ✅ Vision + Text + Multilingual OCR in one pipeline |
| **Focused AI Tool** | ✅ Specific problem (govt docs), not generic chatbot |
| **Rapid Prototyping** | ✅ Built with Gemini API free tier + Ollama |
| **Open-Weight Model** | ✅ Gemma 4 Apache 2.0, self-hostable |
| **Social Impact** | ✅ 400M+ beneficiaries, digital inclusion |
| **Technical Depth** | ✅ Variable token budgets, thinking mode, function calling |

### 📜 License

Apache 2.0 (same as Gemma 4)

### 🙏 Acknowledgments

- Built with [Gemma 4](https://ai.google.dev/gemma) by Google DeepMind
- For [Hacktoberfest Hack Day Noida 2026](https://www.mlh.com/events/hacktoberfest-hack-day-noida)
- Theme: "AI belongs to everyone" 🌍
