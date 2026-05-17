import requests
from scrapers.base import BaseScraper


class ArbeitnowScraper(BaseScraper):
    source_name="Arbeitnow"

    def fetch_jobs(self):
        headers={"User-Agent":"JobAggregator/1.0 (personal project)"}
        response=requests.get("https://www.arbeitnow.com/api/job-board-api", headers=headers)
        data=response.json()
        
        jobs_raw=data["data"] #jobs are inside data key
        jobs=[]
        for job in jobs_raw:
            jobs.append({
            "title":    job.get("title", ""),
            "company":     job.get("company_name", ""),
            "url":         job.get("url", ""),
            "source":      self.source_name,  
            "description": job.get("description", ""),})
            
        return jobs

s = ArbeitnowScraper()
jobs = s.fetch_jobs()
print(len(jobs))
print(jobs[0])

