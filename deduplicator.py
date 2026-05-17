def deduplicate(jobs):
    seen_urls=set()
    unique=[]

    for job in jobs:
        url=job["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(job)
        #if url in seen, do nothing
    return unique
