import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the match
url = "https://fbref.com/en/matches/82e1e5b8/Austin-FC-Minnesota-United-February-24-2024-Major-League-Soccer"

# Send a request to the URL
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

print(soup)