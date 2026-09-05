import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")


def search_jobs(keyword, location):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "results_per_page": 10,
        "what": keyword,
        "where": location,
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        print("Adzuna API Error:", response.status_code)
        print(response.text)
        return []

    data = response.json()

    jobs = []

    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "url": job.get("redirect_url"),
        })

    return jobs


if __name__ == "__main__":
    jobs = search_jobs("Python Developer", "India")

    print("Jobs Found:", len(jobs))

    for job in jobs:
        print("\n-----------------------------")
        print("Title:", job["title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("URL:", job["url"])