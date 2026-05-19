# Job Aggregator

Tired of checking job openings every morning, try this to automate your search. It scrapes sites with public API (you can add any) daily, scores job listings against keywords from your resume, and emails you the best matches automatically.

Built this as a learning project — first time working with APIs, SQLite, and GitHub Actions.

## What it does

- Currently, it scrapes jobs from RemoteOK and Arbeitnow every day (you can expand this to scrape from whichever you like, given the site has public API)
- Removes duplicate listings across both sources
- Scores each job based on how many of your resume keywords show up in the title and description
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
   For Gmail you'll need an App Password, not your actual password. Took me a bit to figure this out — go to Google Account → Security → App Passwords to generate one.

4. Edit `config.py` to add your own resume keywords and target job titles

5. Run it
   ```bash
   python main.py
   ```

## Automated daily runs

There's a GitHub Actions workflow that runs every day at 8 AM so you don't have to think about it. To set it up on your own fork:

1. Fork this repo
2. Go to Settings → Secrets and variables → Actions
3. Add `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, and `RECIPIENT_EMAIL` as secrets
4. That's it — it'll run daily and email you the digest

You can also trigger it manually from the Actions tab if you don't want to wait.

## Adding more scrapers

Create a new file in `scrapers/`, inherit from `BaseScraper`, and implement `fetch_jobs()` to return a list of dicts with these keys: `title`, `company`, `url`, `source`, `description`. Then add it to the list in `main.py`.
