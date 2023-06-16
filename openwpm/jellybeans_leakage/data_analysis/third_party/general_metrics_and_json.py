from pathlib import Path
import sqlite3
from sqlite.enums import ABQueriesBySiteURL, ABQueriesGeneral
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


def generate_json(conn, OUTPUT_PATH: Path):
    # Connect to the SQLite database

    result_json = {}

    for search_engine_name, site_url in SITES:
        SITE_QUERIES = ABQueriesBySiteURL(site_url)

        # First HTTP Requests
        cursor = conn.execute(SITE_QUERIES.HTTPRequests)
        http_requests = query_to_dict(cursor)
        if http_requests:
            # Create the dict for this search engine
            result_json[search_engine_name] = {}
            # Only add keys if there is data
            result_json[search_engine_name]["http_requests"] = http_requests

        # Then Javascripts
        cursor = conn.execute(SITE_QUERIES.JS)
        javascripts = query_to_dict(cursor)
        if javascripts:
            # If it has not been created yet
            if search_engine_name not in result_json:
                result_json[search_engine_name] = {}
            # Only add keys if there is data
            result_json[search_engine_name]["javascripts"] = javascripts

    # Save the leakage details in JSON format
    with open(OUTPUT_PATH, "w") as outfile:
        json.dump(result_json, outfile, indent=4, sort_keys=False)
    print("Document 1 saved in: ", OUTPUT_PATH)


def generate_queries_output(conn, OUTPUT_PATH: Path):
    # List of queries and their explanations
    queries = ABQueriesGeneral.QUERIES

    # Execute the queries and write the results to an output file
    with open(OUTPUT_PATH, "w+") as output_file:
        for section in queries:
            output_file.write(section["explanation"] + "\n")
            for query_info in section["queries"]:
                table_name = query_info["table_name"]
                query = query_info["query"]
                df = pd.read_sql_query(query, conn)
                output_file.write(f"{table_name}:\n")
                output_file.write(df.to_string(index=False) + "\n\n")
    print("Document 2 saved in: ", OUTPUT_PATH)


def main(THIRD_PARTY_DATA_PATH, source, location):
    # First we try only python
    AB_DATA_PATH = Path(f"{source}_adblock/sqlite/[{location}]10_crawls_adblock.sqlite")
    JSON_OUTPUT_PATH = Path(f"results/{source}/[{location}]detail.json")
    QUERIES_OUTPUT_PATH = Path(f"results/{source}/[{location}]general_metrics.txt")

    # We connect to the database
    conn = sqlite3.connect(THIRD_PARTY_DATA_PATH)

    # Attach the second database file
    conn.execute(f"ATTACH DATABASE '{AB_DATA_PATH}' AS adblock")

    generate_json(conn, JSON_OUTPUT_PATH)
    generate_queries_output(conn, QUERIES_OUTPUT_PATH)

    conn.close()


LOCATION = "vpn_czech"
# Third party data path ("main" source of data)
THIRD_PARTY_DATA_PATH = Path(f"sqlite/[{LOCATION}]10_crawls_third_party.sqlite")

main(THIRD_PARTY_DATA_PATH, "python", LOCATION)
main(THIRD_PARTY_DATA_PATH, "js", LOCATION)
