import requests
from scrapers.base import BaseScraper

class RemoteOKScraper(BaseScraper):
    source_name="RemoteOK"

    def fetch_jobs(self):
        headers={"User-Agent":"JobAggregator/1.0 (personal project)"}
        response=requests.get("https://remoteok.com/api", headers=headers)
        data=response.json()
        
        jobs_raw=data[1:] #skipping first item (it is metadata)
        jobs=[]
        for job in jobs_raw:
            jobs.append({
            "title":    job.get("position", ""),
            "company":     job.get("company", ""),
            "url":         job.get("url", ""),
            "source":      self.source_name,  
            "description": job.get("description", ""),})
            
        return jobs

s = RemoteOKScraper()
jobs = s.fetch_jobs()
print(len(jobs))
print(jobs[0])
