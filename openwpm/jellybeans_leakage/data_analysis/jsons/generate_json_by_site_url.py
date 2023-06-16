""" This script generates a JSON file with the details organized by resource site URL. """
from pathlib import Path
import sqlite3
import json
from collections import defaultdict

from sqlite import DetailsQueryBySiteURL

import utils as utils

# TODO: Move this to a setting variable for the whole project
SITES = [
    ("google", "https://www.google.com/search?q=JELLYBEANS"),
    ("bing", "https://www.bing.com/search?q=JELLYBEANS"),
    ("yahoo", "https://search.yahoo.com/search?p=JELLYBEANS"),
    ("duckduckgo", "https://duckduckgo.com/?q=JELLYBEANS"),
    ("yandex", "https://yandex.com/search/?text=JELLYBEANS"),
    ("baidu", "https://www.baidu.com/s?wd=JELLYBEANS"),
    ("naver", "https://search.naver.com/search.naver?query=JELLYBEANS"),
    ("seznam", "https://search.seznam.cz/?q=JELLYBEANS"),
    ("qwant", "https://www.qwant.com/?q=JELLYBEANS"),
    ("aol", "https://search.aol.com/aol/search?q=JELLYBEANS"),
    ("ask", "https://www.ask.com/web?q=JELLYBEANS"),
    ("ecosia", "https://www.ecosia.org/search?q=JELLYBEANS"),
    ("startpage", "https://www.startpage.com/do/dsearch?query=JELLYBEANS"),
    ("sogou", "https://www.sogou.com/web?query=JELLYBEANS"),
    ("swisscows", "https://swisscows.com/web?query=JELLYBEANS"),
]


def prepare_dictionary():
    """Return an empty dictionary with the correct keys for data by site_url and then by type"""
    # Organize the data by search engine
    return {
        search_engine_name: {
            "search_url": search_url,
            "cookies": 0,
            "javascripts": 0,
            "http_requests": 0,
            "data": {
                "cookies": [],
                "javascripts": [],
                "http_requests": [],
            },
        }
        for search_engine_name, search_url in SITES
    }


def generate_overall_details_json(DATA_PATH: Path, OUTPUT_PATH: Path):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATA_PATH)

    data_details = prepare_dictionary()

    for site_name, site_url in SITES:
        SITE_QUERIES = DetailsQueryBySiteURL(site_url)
        site = data_details[site_name]

        # First Cookies
        cookies = conn.execute(SITE_QUERIES.COOKIES).fetchall()
        site["cookies"] = len(cookies)
        for row in cookies:
            row_element = utils.get_processed_cookie_row(row)
            site["data"]["cookies"].append(row_element)

        # Then Javascript
        javascripts = conn.execute(SITE_QUERIES.JS).fetchall()
        site["javascripts"] = len(javascripts)
        for row in javascripts:
            row_element = utils.get_processed_javascript_row(row)
            site["data"]["javascripts"].append(row_element)

        # Lastly HTTP Requests
        http_requests = conn.execute(SITE_QUERIES.HTTPRequests).fetchall()
        site["http_requests"] = len(http_requests)
        for row in http_requests:
            row_element = utils.get_processed_http_request_row(row)
            site["data"]["http_requests"].append(row_element)

    # Save the leakage details in JSON format
    with open(OUTPUT_PATH, "w") as outfile:
        json.dump(data_details, outfile, indent=4, sort_keys=False)
    print("Document saved in: ", OUTPUT_PATH)

    # Close the database connection
    conn.close()


CRAWL_DATA_PATH = Path("../sqlite/10_crawls_results.sqlite")
OUTPUT_PATH = Path("data_details_by_site_url.json")

generate_overall_details_json(CRAWL_DATA_PATH, OUTPUT_PATH)
