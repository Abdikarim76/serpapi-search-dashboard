import os
from pathlib import Path

import requests
from dotenv import load_dotenv


project_folder = Path(__file__).resolve().parent
env_file = project_folder / ".env"

load_dotenv(env_file)

api_key = os.getenv("SERPAPI_API_KEY")

url = "https://serpapi.com/search"

params = {
    "engine": "google",
    "q": "python flask",
    "api_key": api_key
}

response = requests.get(url, params=params)

data = response.json()

print("Status code:", response.status_code)

results = data["organic_results"]

for result in results[:5]:
    print(result["title"])
    print(result["link"])
    print()