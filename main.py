from scrapers.remoteok import RemoteOKScraper
from scrapers.arbeitnow import ArbeitnowScraper
from deduplicator import deduplicate
from scorer import score_job
from database import create_tables, job_exists, save_job
from notifier import send_digest



def run():
    create_tables()

    #1 fetching
    all_jobs=[]

    for Scraper in [RemoteOKScraper, ArbeitnowScraper]:
        try:
            jobs=Scraper().fetch_jobs()
            all_jobs.extend(jobs)
            print(f"[{Scraper.source_name}] Fetched {len(jobs)} jobs") 
        except Exception as e:
            print(f"[{Scraper.source_name}] Error: {e}")

    #2 dedeupicate
    unique_jobs=deduplicate(all_jobs)

    #3 filter jobs already in database
    new_jobs=[j for j in unique_jobs if not job_exists(j["url"])]

    #4 scoring
    scored_jobs=[score_job(j) for j in new_jobs]

    #5 saving to database
    for job in scored_jobs:
        save_job(job)

    #email
    worthy_jobs=[j for j in scored_jobs if j["score"]>=20]
    send_digest(worthy_jobs)

    print(f"Done. {len(scored_jobs)} new, {len(worthy_jobs)} emailed.")

if __name__=="__main__":
    run()


