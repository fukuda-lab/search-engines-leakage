""" This is an independant script that takes any crawled data from OpenWPM and creates new tables and databases with the same data but with filtered by url third party requests only."""

import sqlite3
import pandas as pd
from pathlib import Path
import tldextract

# Add the project's root directory to the system path
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from data_analysis.sqlite import CrawledDataQuery, ThirdPartyTableCreationCommand


def search_third_party(
    table_df: pd.DataFrame,
    table_name: str,
    conn_third_party: sqlite3.Connection,
) -> None:
    """Searches for third party requests in the table_df and adds them to the conn_third_party database."""

    df = table_df.copy()

    # Filter the table_df to only contain the requests made to third parties

    if table_name == "http_requests":
        # http_requests the leakage criteria is strict Second Level Domain matching
        df.loc[:, "top_level_url_second_level_domain"] = df["top_level_url"].apply(
            lambda url: tldextract.extract(url).domain
        )
        df.loc[:, "request_url_second_level_domain"] = df["url"].apply(
            lambda url: tldextract.extract(url).domain
        )

        # Get a series of boolean values that indicate whether the request is to a third party
        requests_to_third_parties = (
            df["top_level_url_second_level_domain"]
            != df["request_url_second_level_domain"]
        )

        # Filter dataframe based on condition (using the series as a mask)
        df = df[requests_to_third_parties]

    elif table_name == "javascripts":
        # javascripts leakage criteria is Second Level Domain between top_level_url and
        # script_url or top_level_url and document_url
        df.loc[:, "top_level_url_second_level_domain"] = df["top_level_url"].apply(
            lambda url: tldextract.extract(url).domain
        )
        df.loc[:, "script_url_second_level_domain"] = df["script_url"].apply(
            lambda url: tldextract.extract(url).domain
        )
        df.loc[:, "document_url_second_level_domain"] = df["document_url"].apply(
            lambda url: tldextract.extract(url).domain
        )

        # Get a series of boolean values that indicate whether the request is to a third party for both cases
        requests_to_third_parties = (
            df["top_level_url_second_level_domain"]
            != df["script_url_second_level_domain"]
        ) | (
            df["top_level_url_second_level_domain"]
            != df["document_url_second_level_domain"]
        )
        # Filter dataframe based on condition (using the series as a mask)
        df = df[requests_to_third_parties]

    elif table_name == "cookies":
        # cookies leakage criteria is Second Level Domain between site_url and host
        df["site_url_second_level_domain"] = df["site_url"].apply(
            lambda url: tldextract.extract(url).domain
        )
        df["host_second_level_domain"] = df["host"].apply(
            lambda url: tldextract.extract(url).domain
        )

        # Get a series of boolean values that indicate whether the request is to a third party
        requests_to_third_parties = (
            df["site_url_second_level_domain"] != df["host_second_level_domain"]
        )

        # Filter dataframe based on condition (using the series as a mask)
        df = df[requests_to_third_parties]

    df_to_write = df.copy()

    # Add the table to the third party database
    df_to_write.to_sql(
        f"{table_name}_third_party",
        conn_third_party,
        if_exists="append",
        index=False,
    )


# Set database paths
CRAWL_DATA_PATH = Path("../sqlite/[vpn_czech]10_crawls_results.sqlite")
THIRD_PARTY_DATA_PATH = Path("sqlite/[vpn_czech]10_crawls_third_party.sqlite")

# Set table names to look for
tables = {
    "http_requests": CrawledDataQuery.HTTP_REQUESTS,
    "javascript": CrawledDataQuery.JS,
    "javascript_cookies": CrawledDataQuery.COOKIES,
}

# Connect to the third party database
conn = sqlite3.connect(CRAWL_DATA_PATH)
third_party_conn = sqlite3.connect(THIRD_PARTY_DATA_PATH)

# Create the tables in the third party database
third_party_conn.execute(ThirdPartyTableCreationCommand.HTTP_REQUESTS)
third_party_conn.execute(ThirdPartyTableCreationCommand.JS)
third_party_conn.execute(ThirdPartyTableCreationCommand.COOKIES)

# Iterate through the tables and search for third party elements
for table_name, query in tables.items():
    third_party_table_name = f"{table_name}_third_party"
    print(f"Searching for third party {table_name}...")
    table_df = pd.read_sql_query(query, conn)
    search_third_party(table_df, table_name, third_party_conn)
    print(f"Done searching for third party {third_party_table_name}.")

print(f"Data collected in {THIRD_PARTY_DATA_PATH}")
