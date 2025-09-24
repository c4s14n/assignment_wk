# assignment_wk

This repository contains automated **API** and **UI** tests with **pytest**.  
Both test types generate reports, and an example report can be found in `tests/reporting_tests/`.

---

## Setup & Run

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate.ps1     # Windows PowerShell

pip install -r requirements.txt

pytest --html=./tests/reporting_tests/report.html --self-contained-html
```

---

## Environment

After cloning or downloading the repo, **rename** the provided file:

```
lc_env  ➝  .env
```

The `.env` file is required for running tests.

## Bugs doc
A detailed list of known issues is documented in QA_Bugs.pdf, available in the repository root.
