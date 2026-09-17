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

    cleaned_results = []

    for result in results[:5]:

        cleaned_result = {
            "title": result.get("title", "No title"),
            "link": result.get("link", "No link"),
            "snippet": result.get("snippet", "No snippet available")
        }

        cleaned_results.append(cleaned_result)

    if not cleaned_results:
        print("No search results were found.")

    else:
        for number, result in enumerate(cleaned_results, start=1):

            print(f"Result {number}")
            print("Title:", result["title"])
            print("Link:", result["link"])
            print("Snippet:", result["snippet"])
            print()

except requests.exceptions.RequestException as error:
    print("Request failed:", error)