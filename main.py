import os
from pathlib import Path

import requests
from dotenv import load_dotenv


project_folder = Path(__file__).resolve().parent
env_file = project_folder / ".env"

load_dotenv(env_file)

api_key = os.getenv("SERPAPI_API_KEY")

search_term = input("What do you want to search for? ")

url = "https://serpapi.com/search"

params = {
    "engine": "google",
    "q": search_term,
    "api_key": api_key
}

try:
    response = requests.get(url, params=params, timeout=10)

    print()
    print("Status code:", response.status_code)
    print()

    response.raise_for_status()

    data = response.json()

    results = data.get("organic_results", [])

    if not results:
        print("No search results were found.")
    else:
        for result in results[:5]:
            print("Title:", result.get("title", "No title"))
            print("Link:", result.get("link", "No link"))
            print("Snippet:", result.get("snippet", "No snippet available"))
            print()

except requests.exceptions.RequestException as error:
    print("Request failed:", error)