# Camera Health Tool

Internal Streamlit app for reviewing camera health, working outage queues, tracking tickets, and using LSU-specific response workflows.

## Setup

1. Create a virtual environment.
2. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Required files

The app expects these project files to exist in the repo:

- `LSU Public Safety Surveillance .csv`
- `data/tiger_eye.png`
- `data/notes.csv`
- `data/device_tracking.csv`
- `data/tickets.csv`
- `data/state_transitions.csv`
- `data/server_roles.csv`

## Optional features

- Tesseract OCR is optional for screenshot/image text extraction.
- An OpenAI API key is optional for AI-assisted ticket extraction features.
