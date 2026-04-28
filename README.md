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

This installs the Streamlit AgGrid dependency used by the app UI. On a fresh machine, make sure the required site-health CSV is present at the repo root as `LSU Public Safety Surveillance .csv` (next to `app.py`) before launch.

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

## Supabase shared storage

The app can sync its editable/history CSV data through Supabase so another computer can use the same notes, tickets, device tracking, transitions, and server-role mapping.

1. In Supabase, open the SQL editor and run `supabase_schema.sql`.
2. Add Streamlit secrets:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-or-service-role-key"
```

The app still writes local CSV files as a fallback/cache. When Supabase secrets and the `app_datasets` table are available, loads prefer Supabase and saves update Supabase.

## Optional features

- Tesseract OCR is optional for screenshot/image text extraction.
- An OpenAI API key is optional for AI-assisted ticket extraction features.
