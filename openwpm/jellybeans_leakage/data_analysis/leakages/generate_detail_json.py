""" This script generates a JSON file with the details of the leakages organized by leakage type and site URL. """

import base64
from pathlib import Path
import sqlite3
import json
from collections import defaultdict
from sqlite import LeakagesDetailsQueryBySiteURL
from ..keyword_encodings import Encodings

# from ..keyword_encoding import get_keyword_encodings
import utils

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

SEARCH_TERMS = ["JELLYBEANS", "jellybeans"]
SEARCH_TERM_ENCODINGS = Encodings(SEARCH_TERMS)

# We are running this script standing in jellybeans_leakage/data_analysis directory
LEAKAGE_DATA_PATH = Path("leakages/sqlite/leakage_data.sqlite")
OUTPUT_PATH = Path("leakages/results/leakages_by_type_and_site_url.json")

# Connect to the SQLite database
conn = sqlite3.connect(LEAKAGE_DATA_PATH)

# Organize the leakage data by leakage_type
# Really useful defaultdict(lambda: defaultdict(list)),
leakage_details = {
    "cookies_leakages": defaultdict(list),
    "javascript_leakages": defaultdict(list),
    "http_requests_leakages": defaultdict(list),
}

for site_url in SITES:
    SITE_QUERIES = LeakagesDetailsQueryBySiteURL(site_url)

    # First Cookies Leakages (least frequent)
    cookies_leakages = conn.execute(SITE_QUERIES.COOKIES).fetchall()
    for row in cookies_leakages:
        leakage_list_element = utils.get_processed_cookie_leakage(row)
        leakage_details["cookies_leakages"][site_url].append(leakage_list_element)

    # Then Javascript Leakages (more frequent)
    javascript_leakages = conn.execute(SITE_QUERIES.JS).fetchall()

    for row in javascript_leakages:
        leakage_list_element = utils.get_processed_javascript_leakage(row)
        leakage_details["javascript_leakages"][site_url].append(leakage_list_element)

    # Lastly HTTP Requests Leakages (most frequent)
    http_requests_leakages = conn.execute(SITE_QUERIES.HTTPRequests).fetchall()
    for row in http_requests_leakages:
        leakage_list_element = utils.get_processed_http_leakage(
            row, SEARCH_TERM_ENCODINGS
        )
        leakage_details["http_requests_leakages"][site_url].append(leakage_list_element)

# Save the leakage details in JSON format
with open(OUTPUT_PATH, "w") as outfile:
    json.dump(leakage_details, outfile, indent=4, sort_keys=False)
print("Document saved in: ", OUTPUT_PATH)

# Close the database connection
conn.close()
