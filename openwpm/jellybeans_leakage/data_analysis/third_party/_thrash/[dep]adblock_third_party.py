from pathlib import Path
import sqlite3
from sqlite.enums import ABPQueriesBySiteURL, ABPQueriesGeneral
import json
import pandas as pd
from pathlib import Path


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


def query_to_dict(query_cursor):
    columns = [column[0] for column in query_cursor.description]
    rows = query_cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def generate_json(adblock_conn, third_party_conn, OUTPUT_PATH: Path):
    # Connect to the SQLite database

    result_json = {
        search_engine_name: {
            "http_requests": [],
            "javascripts": [],
        }
        for search_engine_name, _ in SITES
    }

    for search_engine_name, site_url in SITES:
        SITE_QUERIES = ABPQueriesBySiteURL(site_url)
        search_engine = result_json[search_engine_name]

        # First Javascripts
        cursor = adblock_conn.execute(SITE_QUERIES.JS)
        javascripts = query_to_dict(cursor)
        search_engine["javascripts"].append(javascripts)

        # Lastly HTTP Requests
        cursor = adblock_conn.execute(SITE_QUERIES.HTTPRequests)
        http_requests = query_to_dict(cursor)
        search_engine["http_requests"].append(http_requests)

    # Save the leakage details in JSON format
    with open(OUTPUT_PATH, "w") as outfile:
        json.dump(result_json, outfile, indent=4, sort_keys=False)
    print("Document 1 saved in: ", OUTPUT_PATH)


def generate_queries_output(adblock_conn, third_party_conn, OUTPUT_PATH: Path):
    # List of queries and their explanations
    queries = ABPQueriesGeneral.QUERIES

    # Execute the queries and write the results to an output file
    with open(OUTPUT_PATH, "w+") as output_file:
        for section in queries:
            output_file.write(section["explanation"] + "\n")
            for query_info in section["queries"]:
                table_name = query_info["table_name"]
                query = query_info["query"]
                df_adblock = pd.read_sql_query(query, adblock_conn)
                df_third_party = pd.read_sql_query(query, third_party_conn)
                # Not finished yet, was left inconcluded to try join_two_db.py
                output_file.write(f"{table_name}:\n")
                output_file.write(df.to_string(index=False) + "\n\n")
    print("Document 2 saved in: ", OUTPUT_PATH)


ADBLOCK_DATA_PATH = Path("adblock/sqlite/[tokyo]10_crawls_adblock.sqlite")
THIRD_PARTY_DATA_PATH = Path("sqlite/[tokyo]10_crawls_third_party.sqlite")
JSON_OUTPUT_PATH = Path("results/[tokyo]10_crawls_adblock.json")
QUERIES_OUTPUT_PATH = Path("results/[tokyo]general_metrics.txt")

# We connect to the database
adblock_conn = sqlite3.connect(ADBLOCK_DATA_PATH)
third_party_conn = sqlite3.connect(THIRD_PARTY_DATA_PATH)

generate_json(adblock_conn, JSON_OUTPUT_PATH)
generate_queries_output(adblock_conn, QUERIES_OUTPUT_PATH)

adblock_conn.close()
