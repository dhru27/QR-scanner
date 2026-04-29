# q&a-chatbot

## ME Course Q&A Chatbot (Gemini + Streamlit)

Local AI-powered chatbot that answers questions about a **fictional** course catalog using the **Google Gemini API** (free tier).

## What it can answer (examples)
- Prerequisites: “What are the prerequisites for Robotics & Automation?”
- No prerequisites: “Which courses have no prerequisites?”
- Slot clash: “Do ME401 and ME403 have a slot clash?”
- Credits: “How many credits is CFD?” / “How many credits is ME404?”
- Slot for a course: “Which slot is ME406 in?”
- List courses: “List all courses”

If you ask something **not in the catalog** (e.g., “What is the attendance policy?”), it will respond with a helpful “not available” message.

## Setup
### 1) Create a virtual environment (recommended)
```bash
python -m venv .venv
```

Activate it:
- **Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Add your Gemini API key
Copy `.env.example` to `.env` and fill in your key:
```bash
copy .env.example .env
```

Then edit `.env` and set:
```
GEMINI_API_KEY=...
```

Get a free key from Google AI Studio: `https://aistudio.google.com/`

## Run
```bash
streamlit run app.py
```

## Where the course data lives
The catalog is hardcoded in `course_data.py` as a Python list of dicts.
