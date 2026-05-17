# Job Aggregator

A Python script that scrapes job listings from multiple sites, scores them against your resume keywords, and emails you a daily digest of the best matches.

Built as a learning project.

## What it does

- Scrapes jobs from RemoteOK and Arbeitnow every day
- Removes duplicate listings
- Scores each job based on how many of your resume keywords appear in the title and description
- Emails you the top results sorted by score

## Project structure

```
job_aggregator/
├── config.py          # keywords, email settings
├── database.py        # SQLite storage
├── deduplicator.py    # removes duplicate jobs
├── scorer.py          # scores jobs against your keywords
├── notifier.py        # sends the email digest
├── main.py            # runs everything in order
└── scrapers/
    ├── base.py        # base class all scrapers follow
    ├── remoteok.py    # scrapes RemoteOK API
    └── arbeitnow.py   # scrapes Arbeitnow API
```

## Setup

1. Clone the repo
   ```bash
   git clone https://github.com/mkyadav2021/job-aggregator.git
   cd job-aggregator
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file (use `.env.example` as a template)
   ```
   EMAIL_ADDRESS=your_gmail@gmail.com
   EMAIL_PASSWORD=your_app_password
   RECIPIENT_EMAIL=where_to_send@gmail.com
   ```
   For Gmail, you need an App Password — not your real password. Go to Google Account → Security → App Passwords to generate one.

4. Edit `config.py` to set your resume keywords and target job titles

5. Run it
   ```bash
   python main.py
   ```

## Automated daily runs

The project includes a GitHub Actions workflow that runs every day at 8 AM automatically. To use it:

1. Fork this repo
2. Go to Settings → Secrets and variables → Actions
3. Add `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, and `RECIPIENT_EMAIL` as secrets
4. The workflow will run daily and email you the digest

You can also trigger it manually from the Actions tab.

## Adding more scrapers

Create a new file in `scrapers/`, inherit from `BaseScraper`, and implement `fetch_jobs()` to return a list of dicts with these keys: `title`, `company`, `url`, `source`, `description`. Then add it to the list in `main.py`.
