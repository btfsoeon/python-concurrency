import argparse
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count

 
def fetch(dir, link):
    response = requests.get(link)
    with open(dir+"/"+link.split("/")[-1]+".html", "wb") as f:
        f.write(response.content)


def get_links():
    countries_list = 'https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)'
    all_links = []
    response = requests.get(countries_list)
    soup = BeautifulSoup(response.text, "lxml")
    countries_el = soup.select('td .flagicon+ a')
    for link_el in countries_el:
        link = link_el.get("href")
        link = urljoin(countries_list, link)
        all_links.append(link)
    return all_links


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("type", type=int, help="0: single-thread, 1: multi-thread, 2: multi-core")
    args = parser.parse_args()
    
    links = get_links()
    print(f"Total pages: {len(links)}")
    start_time = time.time()
    
    # This for loop will be optimized
    if args.type == 0:
        for link in links:
            fetch("naive", link)
    elif args.type == 1:
        with ThreadPoolExecutor(max_workers=16) as executor:
            # executor.map(fetch, "multithread", links)
            future_fetch = {executor.submit(fetch, "multithread", link): link for link in links}
            for future in as_completed(future_fetch):
                link = future_fetch[future]
                try:
                    data = future.result()
                except Exception as e:
                    print(f"Exception occurred: {link}, {e}")
    elif args.type == 2:
        print(f"cpu count: {cpu_count()}")
        with Pool(cpu_count()) as p:
            # p.map(fetch, links)
            {p.apply(fetch, args =("multiprocess", link)): link for link in links}
 
    duration = time.time() - start_time
    print(f"Downloaded {len(links)} links in {duration} seconds")
    