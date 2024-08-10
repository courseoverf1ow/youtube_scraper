import json
import time
import unicodedata

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def parse_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: makes the browser window invisible
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_video(driver, url, selectors, pages_to_scrape=10, wait_time=2):
    driver.get(url)
    videoHash = ""
    try:
        for _ in range(pages_to_scrape):
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for a in soup.find_all("a", href=True):
                val = a["href"]
                if val.startswith("/watch?v="):
                    videoHash = val.split("v=")[1]
                    videoHash = videoHash.split('&')[0]
                    break
    finally:
        driver.quit()

    return videoHash


with open('video.json', 'r') as file:
    data = json.load(file)

playlist = data['playlist']

for item in playlist:
    title = item['title']
    topics = item['topic']
    print(f"Title: {title}")
    print("Topics:")
    videoHashList = []
    for topic in topics:
        videoHash = get_video(
            setup_driver(),
            f"https://www.youtube.com/results?search_query={topic}&sp=CAASBBABGAM%253D",
            ("div", "ytd-item-section-renderer"),
            1,
            2
        )
        print(f"Video Hash: {videoHash}")
        videoHashList.append(videoHash)
        print(f"- {topic}")
    item['videos'] = videoHashList
    del item['topic']

with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)
