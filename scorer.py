from config import RESUME_KEYWORDS

def score_job(job):
    text=(job["title"]+" "+job.get("description","")).lower()

    matches=[kw for kw in RESUME_KEYWORDS if kw in text]

    score=int((len(matches)/len(RESUME_KEYWORDS))*100)

    job["score"]=score
    job["matched_keywords"] = matches
    return job
