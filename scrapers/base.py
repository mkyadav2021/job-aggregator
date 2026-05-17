class BaseScraper:
    source_name="unknown"

    def fetch_jobs(self):
        raise NotImplementedError