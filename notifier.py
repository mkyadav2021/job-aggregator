import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL

def send_digest(jobs):
    if not jobs:
        return
    
    jobs=sorted(jobs, key=lambda j:j["score"], reverse=True)

    html="<h2>Today's Job Digest</h2>"

    for job in jobs[:40]:
        html+=  f"""
        <div style="margin-bottom:15px; padding:10px; border-left:3px solid #2563eb;">
            <strong>{job['title']}</strong> at {job['company']}<br>
            Score: {job['score']}% | Keywords: {', '.join(job.get('matched_keywords', []))}<br>
            <a href="{job['url']}">View Job</a>
        </div>
        """

    msg=MIMEMultipart("alternative")
    msg["Subject"] = f"Job Digest, {len(jobs)} new listings"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls() #for encryption
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

if __name__ == "__main__":
    fake_jobs = [
        {
            "title": "Python Developer",
            "company": "Test Corp",
            "url": "https://example.com/job/1",
            "score": 80,
            "matched_keywords": ["python", "django"],
        }
    ]
    send_digest(fake_jobs)
    print("Email sent!")
