""" This file is used to search for the actual leakages in the crawled data (HTTP requests, JavaScripts, and Cookies).

If we were to have perfomance issues, we could consider adding the eTLD+1's to the crawl_data database schema and save them at crawling time, so we can make the filtering in the SQL query in stead of relying on pandas dataframe.
"""

import base64
import sqlite3
import pandas as pd
from pathlib import Path
from keyword_encodings import Encodings
import tldextract
from sqlite import (
    CrawledDataQuery,
    LeakageTableCreationCommand,
    LeakageDataQueries,
    ColumnsToSearch,
    LeakageTableNames,
)

CRAWL_DATA_PATH = Path("sqlite/crawl_results.sqlite")
LEAKAGE_DATA_PATH = Path("leakages/sqlite/leakage_data.sqlite")
SEARCH_TERMS = ["JELLYBEANS", "jellybeans"]
SEARCH_TERM_ENCODINGS = Encodings(SEARCH_TERMS)


def search_leakage(
    table_df: pd.DataFrame, column: str, table_name: str, conn_leak: sqlite3.Connection
) -> None:
    """Evaluates the existence of leakage in a given column among all of the entries of the given table_df.
    The criteria used is Second-Level Domain difference."""

    # Traverse all encodings
    for keyword in SEARCH_TERMS:
        # TODO: If found, add the actual keyword (lowercase or uppercase) to the leakage table
        for encoding_name, encoded_term in SEARCH_TERM_ENCODINGS.encodings[
            keyword
        ].items():
            # Filter the table_df to only contain the requests made to third parties

            if table_name == LeakageTableNames.HTTP_REQUESTS:
                # http_requests the leakage criteria is strict Second Level Domain matching
                table_df["top_level_url_second_level_domain"] = table_df[
                    "top_level_url"
                ].apply(lambda url: tldextract.extract(url).domain)
                table_df["request_url_second_level_domain"] = table_df["url"].apply(
                    lambda url: tldextract.extract(url).domain
                )

                # Get a series of boolean values that indicate whether the request is to a third party
                requests_to_third_parties = (
                    table_df["top_level_url_second_level_domain"]
                    != table_df["request_url_second_level_domain"]
                )

                # Filter dataframe based on condition (using the series as a mask)
                table_df = table_df[requests_to_third_parties]

            # TODO: Add the corresponding cases for JS and Cookies, after discussing my two questions from Slack

            # Get a series of boolean True values for the rows that contain the search term with the actual evaluated encoding
            leakages_index_series: pd.Series = table_df[column].str.contains(
                encoded_term, na=False, case=False
            )
            leakages = table_df[leakages_index_series]
            if not leakages.empty:
                print(
                    f"Leakages found in {column} with search encoded_term:"
                    f" {encoded_term}"
                )
                # Add the encoding and site_url to the leakages DataFrame
                leakages["encoding"] = encoding_name
                leakages["site_url"] = table_df["site_url"]
                leakages.to_sql(table_name, conn_leak, if_exists="append", index=False)


# Connect to the SQLite database
conn = sqlite3.connect(CRAWL_DATA_PATH)

# Read the data into separate pandas DataFrames
http_requests_data = pd.read_sql_query(CrawledDataQuery.HTTP_REQUESTS, conn)
javascript_data = pd.read_sql_query(CrawledDataQuery.JS, conn)
javascript_cookies_data = pd.read_sql_query(CrawledDataQuery.COOKIES, conn)

# New encodings:
# We could use Ciphey as  paper suggests, but we will add them manually for now


# Connect to the SQLite database for leakage data
conn_leak = sqlite3.connect(LEAKAGE_DATA_PATH)

# Create leakage tables
conn_leak.execute(LeakageTableCreationCommand.HTTP_REQUESTS)
conn_leak.execute(LeakageTableCreationCommand.JS)
conn_leak.execute(LeakageTableCreationCommand.COOKIES)

conn_leak.commit()

# Search for leakage in relevant columns
crawled_data_dict = {
    "tables": [http_requests_data, javascript_data, javascript_cookies_data],
    "columns": [
        ColumnsToSearch.HTTP_REQUESTS.value,
        ColumnsToSearch.JS.value,
        ColumnsToSearch.COOKIES.value,
    ],
    "table_names": [
        LeakageTableNames.HTTP_REQUESTS,
        LeakageTableNames.JS,
        LeakageTableNames.COOKIES,
    ],
}

print("Starting leakage search... \n")

for i in range(3):
    table = crawled_data_dict["tables"][i]
    columns = crawled_data_dict["columns"][i]
    table_name = crawled_data_dict["table_names"][i]
    print(f"Starting table {table_name}...\n")
    for j, column in enumerate(columns):
        search_leakage(table, column, table_name, conn_leak)
        print(f"Finished column {column} of table ({i+1})/{3}) ({j+1}/{len(columns)})")


# Write about general crawling results
queries = LeakageDataQueries.QUERIES

with open("leakages/results/crawl_data_metrics.txt", "w") as output_file:
    for section in queries:
        output_file.write(section["explanation"] + "\n")
        for query_info in section["queries"]:
            table_name = query_info["table_name"]
            query = query_info["query"]
            df = pd.read_sql_query(query, conn)
            output_file.write(df.to_string(index=False) + "\n\n")

conn.close()
conn_leak.close()
