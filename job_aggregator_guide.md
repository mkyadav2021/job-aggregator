# Job Listing Aggregator — Build Guide

A step-by-step roadmap to build a Python tool that scrapes job listings,
removes duplicates, scores them against your resume, and emails you a daily digest.

---

## Project Structure (what you'll end up with)

```
job_aggregator/
├── config.py          # your settings (keywords, email creds, target sites)
├── scrapers/
│   ├── __init__.py
│   ├── base.py        # base scraper class
│   ├── remoteok.py    # scraper for RemoteOK
│   └── arbeitnow.py   # scraper for Arbeitnow
├── deduplicator.py    # removes duplicate postings
├── scorer.py          # scores jobs against your resume keywords
├── notifier.py        # sends the email digest
├── database.py        # stores jobs in SQLite
├── main.py            # ties everything together
└── requirements.txt
```

---

## Step 0 — Set Up Your Environment

**What to do:**

1. Create a project folder called `job_aggregator/`.
2. Create a virtual environment and activate it.
3. Create `requirements.txt` with these libraries:

```
requests
beautifulsoup4
schedule
python-dotenv
```

4. Run `pip install -r requirements.txt`.
5. Create a `.env` file for secrets (email password etc.). Never commit this.

**Why these libraries?**
- `requests` — makes HTTP calls to websites.
- `beautifulsoup4` — parses HTML to pull out job data.
- `schedule` — runs your script on a timer (daily).
- `python-dotenv` — loads secrets from `.env` so you don't hardcode passwords.

---

## Step 1 — Config File

**What to do:** Create `config.py` to hold all your settings in one place.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Keywords from your resume (lowercase)
RESUME_KEYWORDS = [
    "python", "django", "flask", "sql", "rest api",
    "git", "docker", "javascript",
]

# Job titles you're looking for
TARGET_TITLES = ["junior developer", "python developer", "backend developer"]

# Email settings (use App Passwords for Gmail, not your real password)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
```

**Hint:** For Gmail, Google blocks normal passwords. Search "Gmail App Password"
and generate one — that's what goes in your `.env`.

---

## Step 2 — Database (SQLite Storage)

**What to do:** Create `database.py` to store every job you find.
This prevents re-processing old jobs and lets you track history.

**Key concepts to use:**
- `sqlite3` (built-in, no install needed).
- Create a table with columns: `id`, `title`, `company`, `url`, `source`,
  `date_found`, `score`.
- Write two functions: `save_job(job)` and `job_exists(url)`.

**Hint:** Use the job `url` as the unique identifier — if the URL already exists
in your database, you've seen this job before.

```python
# Skeleton to get you started
import sqlite3

DB_NAME = "jobs.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def create_tables():
    """Run this once at startup to ensure the table exists."""
    # YOUR CODE: CREATE TABLE IF NOT EXISTS jobs (...)
    pass

def job_exists(url):
    """Return True if this URL is already in the database."""
    # YOUR CODE: SELECT 1 FROM jobs WHERE url = ?
    pass

def save_job(job_dict):
    """Insert a job dict into the database."""
    # YOUR CODE: INSERT INTO jobs ...
    pass
```

---

## Step 3 — Build Your First Scraper

**What to do:** Start with ONE site. Get it working end-to-end before adding more.

**Recommended starter site:** RemoteOK (`https://remoteok.com/api`)
— it has a free JSON API, so you don't even need BeautifulSoup yet.

Create `scrapers/base.py`:

```python
# A base class that all scrapers will follow
class BaseScraper:
    source_name = "unknown"

    def fetch_jobs(self):
        """Return a list of job dicts with keys:
        title, company, url, location, description, source
        """
        raise NotImplementedError
```

Create `scrapers/remoteok.py`:

```python
import requests
from scrapers.base import BaseScraper

class RemoteOKScraper(BaseScraper):
    source_name = "RemoteOK"

    def fetch_jobs(self):
        # Hint: requests.get("https://remoteok.com/api")
        # The response is JSON — a list of dicts.
        # The first item is metadata, skip it.
        # Each job dict has keys like: position, company, url, description
        # Normalize them into YOUR standard format and return a list.
        pass
```

**Important:** Always set a `User-Agent` header in your requests:
```python
headers = {"User-Agent": "JobAggregator/1.0 (personal project)"}
```
Some sites block the default Python user-agent.

**After this step, test it:**
```python
s = RemoteOKScraper()
jobs = s.fetch_jobs()
print(f"Found {len(jobs)} jobs")
print(jobs[0])  # inspect one job
```

---

## Step 4 — Add a Second Scraper (HTML Parsing)

**What to do:** Now add a site that requires actual HTML parsing so you learn
BeautifulSoup. Good beginner-friendly option: Arbeitnow (`https://www.arbeitnow.com/api/job-board-api`).

Create `scrapers/arbeitnow.py` following the same `BaseScraper` pattern.

**Hint — BeautifulSoup basics you'll need:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_text, "html.parser")
# Find elements:  soup.find("div", class_="job-card")
# Find all:       soup.find_all("a", class_="job-link")
# Get text:       element.get_text(strip=True)
# Get attribute:  element["href"]
```

If the site also has a JSON API, even better — use that instead.
The goal is just to have 2+ sources feeding into the same pipeline.

---

## Step 5 — Deduplication

**What to do:** Create `deduplicator.py`. Jobs appear on multiple boards,
so the same role shows up twice. Remove duplicates.

**Strategy (simple → advanced):**

1. **Exact URL match** — easiest. Same URL = same job. Your database
   `job_exists()` already handles this.

2. **Fuzzy title + company match** — catches cross-posted jobs with
   slightly different URLs.

**Hint for fuzzy matching:**
```python
# Option A: Simple — normalize and compare
def normalize(text):
    return text.lower().strip().replace("  ", " ")

# Option B: Use difflib (built-in)
from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.85
```

Write a function `deduplicate(jobs)` that takes a list and returns a
smaller list with duplicates removed.

---

## Step 6 — Resume Keyword Scorer

**What to do:** Create `scorer.py`. For each job, check how many of your
resume keywords appear in the job title + description. More matches = higher score.

```python
# scorer.py
from config import RESUME_KEYWORDS

def score_job(job):
    """Return a score (0-100) based on keyword matches."""
    text = (job["title"] + " " + job.get("description", "")).lower()

    matches = [kw for kw in RESUME_KEYWORDS if kw in text]
    # Score = percentage of your keywords that matched
    score = int((len(matches) / len(RESUME_KEYWORDS)) * 100)

    job["score"] = score
    job["matched_keywords"] = matches
    return job
```

**Ideas to improve later:**
- Weight title matches higher than description matches.
- Add negative keywords (e.g., "senior", "10+ years") that lower the score.
- Boost score if the job title matches your `TARGET_TITLES`.

---

## Step 7 — Email Notifier

**What to do:** Create `notifier.py` to send yourself an HTML email digest.

**Hint — use `smtplib` and `email.mime` (both built-in):**

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL

def send_digest(jobs):
    """Send an email with today's top jobs."""
    if not jobs:
        return

    # Sort by score, highest first
    jobs = sorted(jobs, key=lambda j: j["score"], reverse=True)

    # Build HTML body
    # Hint: loop through jobs, create a simple HTML list/table
    # Show: title, company, score, matched keywords, link

    html = "<h2>Today's Job Digest</h2>"
    for job in jobs[:20]:  # top 20
        html += f"""
        <div style="margin-bottom:15px; padding:10px; border-left:3px solid #2563eb;">
            <strong>{job['title']}</strong> at {job['company']}<br>
            Score: {job['score']}% | Keywords: {', '.join(job.get('matched_keywords', []))}<br>
            <a href="{job['url']}">View Job</a>
        </div>
        """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Digest — {len(jobs)} new listings"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    # Hint: use smtp.gmail.com, port 587, starttls
    # YOUR CODE: connect, login, send, quit
```

**Test this step in isolation** — send yourself a dummy email before connecting
it to the real pipeline.

---

## Step 8 — Main Pipeline

**What to do:** Create `main.py` that runs the full flow:

```
fetch → deduplicate → score → save to DB → email top results
```

```python
# main.py
from scrapers.remoteok import RemoteOKScraper
from scrapers.arbeitnow import ArbeitnowScraper
from deduplicator import deduplicate
from scorer import score_job
from database import create_tables, job_exists, save_job
from notifier import send_digest

def run():
    create_tables()

    # 1. Fetch from all sources
    all_jobs = []
    for Scraper in [RemoteOKScraper, ArbeitnowScraper]:
        try:
            jobs = Scraper().fetch_jobs()
            all_jobs.extend(jobs)
            print(f"[{Scraper.source_name}] Fetched {len(jobs)} jobs")
        except Exception as e:
            print(f"[{Scraper.source_name}] Error: {e}")

    # 2. Deduplicate
    unique_jobs = deduplicate(all_jobs)

    # 3. Filter out jobs already in DB
    new_jobs = [j for j in unique_jobs if not job_exists(j["url"])]

    # 4. Score each job
    scored_jobs = [score_job(j) for j in new_jobs]

    # 5. Save to database
    for job in scored_jobs:
        save_job(job)

    # 6. Email digest (only jobs scoring above threshold)
    worthy_jobs = [j for j in scored_jobs if j["score"] >= 20]
    send_digest(worthy_jobs)

    print(f"Done. {len(scored_jobs)} new, {len(worthy_jobs)} emailed.")

if __name__ == "__main__":
    run()
```

---

## Step 9 — Schedule It Daily

**What to do:** Make it run automatically every day.

**Option A — `schedule` library (simple, must stay running):**
```python
import schedule
import time

schedule.every().day.at("08:00").do(run)

while True:
    schedule.pending_jobs()  # Hint: the actual method is schedule.run_pending()
    time.sleep(60)
```

**Option B — cron job (Linux/Mac, better for production):**
```bash
# Run every day at 8 AM
0 8 * * * cd /path/to/job_aggregator && /path/to/venv/bin/python main.py
```

**Option C — Windows Task Scheduler** if you're on Windows.

---

## Step 10 — Polish & Extend

Once the core works, improve it incrementally:

- **Add logging** — replace `print()` with Python's `logging` module.
- **Add error handling** — wrap each scraper in try/except so one failure
  doesn't kill the whole run.
- **Rate limiting** — add `time.sleep(2)` between requests to be polite.
- **More scrapers** — LinkedIn (hard, needs auth), Indeed, HackerNews
  "Who is Hiring" threads.
- **Better scoring** — use TF-IDF from `scikit-learn` to compare your
  resume text against job descriptions.
- **CLI arguments** — use `argparse` to run specific scrapers or force
  an email send.
- **Dashboard** — build a simple Flask app to browse your job database
  in a browser.

---

## Quick Reference — Order of Implementation

| Step | File              | Est. Time | Difficulty |
|------|-------------------|-----------|------------|
| 0    | Environment setup | 15 min    | Easy       |
| 1    | config.py         | 10 min    | Easy       |
| 2    | database.py       | 30 min    | Easy       |
| 3    | First scraper     | 45 min    | Medium     |
| 4    | Second scraper    | 30 min    | Medium     |
| 5    | deduplicator.py   | 20 min    | Easy       |
| 6    | scorer.py         | 20 min    | Easy       |
| 7    | notifier.py       | 40 min    | Medium     |
| 8    | main.py           | 20 min    | Easy       |
| 9    | Scheduling        | 15 min    | Easy       |

**Total: ~4-5 hours** for a working v1.

---

## Rules for Yourself

1. **Build one step at a time.** Test each piece before moving on.
2. **Print everything.** When debugging scrapers, print the raw response first.
3. **Start small.** Get 1 scraper → database → print working before adding email.
4. **Read the docs.** When stuck on BeautifulSoup or smtplib, their official
   docs are beginner-friendly.
5. **Be polite to servers.** Add delays between requests. Set a proper User-Agent.
   Don't scrape sites that explicitly forbid it in their robots.txt.
