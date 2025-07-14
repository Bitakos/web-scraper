import requests
from bs4 import BeautifulSoup
import threading
import queue
import json
import time

# GLOBAL VARIABLES
BASE_URL = "https://news.ycombinator.com/news?p="
NUM_PAGES = 5  # Number of pages to scrape
THREAD_COUNT = 3
OUTPUT_FILE = "hacker_news.json"

# Thread-safe queue
page_queue = queue.Queue()
results = []
results_lock = threading.Lock()

def fetch_and_parse(page_number):
    try:
        response = requests.get(BASE_URL + str(page_number))
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = soup.select(".titleline")
        page_results = []

        for title_tag in titles:
            if title_tag.a:
                title = title_tag.a.get_text()
                link = title_tag.a['href']
                page_results.append({'title': title, 'link': link})
        
        with results_lock:
            results.extend(page_results)

    except Exception as e:
        print(f"[!] Error on page {page_number}: {e}")

def worker():
    while not page_queue.empty():
        page_number = page_queue.get()
        print(f"[THREAD {threading.current_thread().name}] Scraping page {page_number}")
        fetch_and_parse(page_number)
        page_queue.task_done()

def main():
    start_time = time.time()
    
    for i in range(1, NUM_PAGES + 1):
        page_queue.put(i)

    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    page_queue.join()

    for t in threads:
        t.join()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Scraped {len(results)} articles in {round(time.time() - start_time, 2)}s")
    print(f"📝 Results saved to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
