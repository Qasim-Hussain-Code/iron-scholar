# The Iron Scholar

*Mens sana in corpore sano.*

A single-file Streamlit application that unifies a training ledger with a
study companion. It provides a structured weekly programme, session logging,
a daily adherence ledger, a rest timer that interleaves spaced-repetition
flashcards (bioinformatics, immunology, machine learning) between sets, a
nutrition reference, lipid-panel tracking, an equipment directory, and a
curated library of open-access resources.

## Layout

```
Iron_Scholar_App/
    app.py                  the entire application
    requirements.txt        streamlit, pandas, plotly, supabase
    .streamlit/
        config.toml         theme (Streamlit reads it only from this path)
    docs/                   supplementary notes
    .gitignore
    README.md
```

## Running locally

Requires Python 3.10 or newer.

```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app is served at http://localhost:8501. With no secrets configured the
app runs in local file mode, writing everything to a data.json beside app.py.
That file is gitignored and never leaves the machine.

## Cloud storage setup

Optional. Without it the app still works in local file mode. With it, your
records survive every restart, redeploy and sleep cycle on Streamlit
Community Cloud, whose disk is otherwise wiped.

Step one, create the table. In the Supabase SQL editor, run this once:

```sql
create table if not exists iron_scholar (
  id bigint primary key,
  data jsonb not null,
  updated_at timestamptz default now()
);
insert into iron_scholar (id, data) values (1, '{}'::jsonb)
on conflict (id) do nothing;
```

Step two, supply the secrets. Locally they belong in
`.streamlit/secrets.toml`, which is gitignored and must never be committed:

```toml
SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
SUPABASE_KEY = "YOUR-ANON-OR-SERVICE-KEY"
APP_PASSCODE = "choose-a-passcode"
```

`APP_PASSCODE` is optional. When present, the app asks for it once before
rendering anything, which puts a curtain over a public URL. Leave the line
out entirely and there is no gate.

On Streamlit Community Cloud the same block is pasted into the app's
settings rather than a file: open the app, choose Manage app, then Settings,
then Secrets, paste the block, and save. The app reboots and picks them up.

Step three, confirm. Open Data and Settings. It reads either
"Cloud connected" or "Local file mode". If cloud storage is configured but
unreachable, the page says so, names the reason, and the app keeps working
against the local file so nothing is lost. To migrate existing records,
upload an old data.json under Restore from backup once; it becomes the
contents of the active store.

## Disclaimers

The training material is intended for a healthy adult beginner; discontinue
any exercise that provokes sharp pain. The health page supports educational
self-tracking and is not medical advice. Interpret lipid panels and all
clinical values with a qualified physician.


