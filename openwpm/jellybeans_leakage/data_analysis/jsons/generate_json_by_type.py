""" This script generates a JSON file with the details organized by resource type. """

import base64
from pathlib import Path
import sqlite3
import json
from collections import defaultdict

from sqlite import DetailsQueryBySiteURL

import utils as utils

# TODO: Move this to a setting variable for the whole project
SITES = [
    "https://www.google.com/search?q=JELLYBEANS",
    "https://www.bing.com/search?q=JELLYBEANS",
    "https://search.yahoo.com/search?p=JELLYBEANS",
    "https://duckduckgo.com/?q=JELLYBEANS",
    "https://yandex.com/search/?text=JELLYBEANS",
    "https://www.baidu.com/s?wd=JELLYBEANS",
    "https://search.naver.com/search.naver?query=JELLYBEANS",
    "https://search.seznam.cz/?q=JELLYBEANS",
    "https://www.qwant.com/?q=JELLYBEANS",
    "https://search.aol.com/aol/search?q=JELLYBEANS",
    "https://www.ask.com/web?q=JELLYBEANS",
    "https://www.ecosia.org/search?q=JELLYBEANS",
    "https://www.startpage.com/do/dsearch?query=JELLYBEANS",
    "https://www.sogou.com/web?query=JELLYBEANS",
    "https://swisscows.com/web?query=JELLYBEANS",
]


def generate_overall_details_json(DATA_PATH: Path, OUTPUT_PATH: Path):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATA_PATH)

    # Organize the leakage data by leakage_type and site_url
    data_details = {
        "cookies": defaultdict(lambda: defaultdict(list)),
        "javascripts": defaultdict(lambda: defaultdict(list)),
        "http_requests": defaultdict(lambda: defaultdict(list)),
    }

    cookies_amount = 0
    javascripts_amount = 0
    http_requests_amount = 0

    for site_url in SITES:
        SITE_QUERIES = DetailsQueryBySiteURL(site_url)

        # First Cookies Leakages (least frequent)
        cookies = conn.execute(SITE_QUERIES.COOKIES).fetchall()
        cookies_amount += len(cookies)
        for row in cookies:
            row_element = utils.get_processed_cookie_row(row)
            data_details["cookies"]["data"][site_url].append(row_element)

        # Then Javascript Leakages (more frequent)
        javascripts = conn.execute(SITE_QUERIES.JS).fetchall()
        javascripts_amount += len(javascripts)
        for row in javascripts:
            row_element = utils.get_processed_javascript_row(row)
            data_details["javascripts"]["data"][site_url].append(row_element)

        # Lastly HTTP Requests Leakages (most frequent)
        http_requests = conn.execute(SITE_QUERIES.HTTPRequests).fetchall()
        http_requests_amount += len(http_requests)
        for row in http_requests:
            row_element = utils.get_processed_http_request_row(row)
            data_details["http_requests"]["data"][site_url].append(row_element)
    data_details["cookies"]["amount"] = cookies_amount
    data_details["javascripts"]["amount"] = javascripts_amount
    data_details["http_requests"]["amount"] = http_requests_amount

    # Save the leakage details in JSON format
    with open(OUTPUT_PATH, "w") as outfile:
        json.dump(data_details, outfile, indent=4, sort_keys=False)
    print("Document saved in: ", OUTPUT_PATH)

    # Close the database connection
    conn.close()


CRAWL_DATA_PATH = Path("../sqlite/10_crawls_results.sqlite")
OUTPUT_PATH = Path("data_details_by_type.json")

generate_overall_details_json(CRAWL_DATA_PATH, OUTPUT_PATH)
