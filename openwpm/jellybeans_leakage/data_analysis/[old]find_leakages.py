""" This file is used to search for the actual leakages in the crawled data (HTTP requests, JavaScripts, and Cookies).
If we were to have perfomance issues, we could consider adding the eTLD+1's to the crawl_data database schema and save them at crawling time, so we can make the filtering in the SQL query in stead of relying on pandas dataframe.
"""
# TODO: Fix loc warnings if pretending to use the ids as index

import sqlite3
import pandas as pd
from pathlib import Path
import tldextract

# We are running this script standing in parent directory (leakage_processing.py file)
from data_analysis.leakages.keyword_encodings import Encodings
from data_analysis.sqlite import (
    CrawledDataQuery,
    LeakageTableCreationCommand,
    LeakageDropTableCommand,
    LeakageDataQueries,
    ColumnsToSearch,
    LeakageTableNames,
)

# CRAWL_DATA_PATH = Path("sqlite/[vpn_czech]10_crawls_results.sqlite")
SEARCH_TERMS = ["JELLYBEANS"]
SEARCH_TERMS_ENCODINGS = Encodings(SEARCH_TERMS)


def search_leakage(
    table_df: pd.DataFrame, column: str, table_name: str, conn_leak: sqlite3.Connection
) -> None:
    """Evaluates the existence of leakage in a given column among all of the entries of the given table_df.
    The criteria used is Second-Level Domain difference."""

    # Traverse all search_terms (just one for now)
    for keyword in SEARCH_TERMS_ENCODINGS.search_terms:
        # Traverse original and lowercase
        for keyword_case in SEARCH_TERMS_ENCODINGS.encodings[keyword].keys():
            # Traverse all encodings for the current search term and case
            for encoding_name, encoded_term in SEARCH_TERMS_ENCODINGS.encodings[
                keyword
            ][keyword_case].items():
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

                elif table_name == LeakageTableNames.JS:
                    # javascripts leakage criteria is Second Level Domain between top_level_url and
                    # script_url or top_level_url and document_url
                    table_df["top_level_url_second_level_domain"] = table_df[
                        "top_level_url"
                    ].apply(lambda url: tldextract.extract(url).domain)
                    table_df["script_url_second_level_domain"] = table_df[
                        "script_url"
                    ].apply(lambda url: tldextract.extract(url).domain)
                    table_df["document_url_second_level_domain"] = table_df[
                        "document_url"
                    ].apply(lambda url: tldextract.extract(url).domain)

                    # Get a series of boolean values that indicate whether the request is to a third party for both cases
                    requests_to_third_parties = (
                        table_df["top_level_url_second_level_domain"]
                        != table_df["script_url_second_level_domain"]
                    ) | (
                        table_df["top_level_url_second_level_domain"]
                        != table_df["document_url_second_level_domain"]
                    )
                    # Filter dataframe based on condition (using the series as a mask)
                    table_df = table_df[requests_to_third_parties]

                elif table_name == LeakageTableNames.COOKIES:
                    # cookies leakage criteria is Second Level Domain between site_url and host
                    table_df["site_url_second_level_domain"] = table_df[
                        "site_url"
                    ].apply(lambda url: tldextract.extract(url).domain)
                    table_df["host_second_level_domain"] = table_df["host"].apply(
                        lambda url: tldextract.extract(url).domain
                    )

                    # Get a series of boolean values that indicate whether the request is to a third party
                    requests_to_third_parties = (
                        table_df["site_url_second_level_domain"]
                        != table_df["host_second_level_domain"]
                    )

                    # Filter dataframe based on condition (using the series as a mask)
                    table_df = table_df[requests_to_third_parties]

                # Get a series of boolean True values for the rows that contain the search term with the actual evaluated encoding
                leakages_index_series: pd.Series = table_df[column].str.contains(
                    encoded_term,
                    na=False,
                    case=True,  # We are handling the casing in the SEARCH_TERMS_ENCODINGS, so we set this to True to avoid duplicates
                )
                leakages = table_df[leakages_index_series]
                if not leakages.empty:
                    print(
                        f"Leakages found in {column} with search encoded_term:"
                        f" {encoded_term}"
                    )
                    # Add the encoding and site_url to the leakages DataFrame
                    if keyword_case == "lowercase":
                        encoding_name = encoding_name + "_lowercase"
                    leakages["encoding"] = encoding_name
                    leakages["site_url"] = table_df["site_url"]
                    leakages.to_sql(
                        table_name, conn_leak, if_exists="append", index=False
                    )


def find_leakages(
    CRAWL_DATA_PATH: Path, LEAKAGE_DATA_PATH: Path, OVERALL_OUTPUT_PATH: Path
):
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

    # Drop previous leakage tables
    conn_leak.execute(LeakageDropTableCommand.HTTP_REQUESTS)
    conn_leak.execute(LeakageDropTableCommand.JS)
    conn_leak.execute(LeakageDropTableCommand.COOKIES)

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
            print(
                f"Finished column {column} of table ({i+1})/{3}) ({j+1}/{len(columns)})"
            )

    # Write about general crawling results
    queries = LeakageDataQueries.QUERIES

    with open(OVERALL_OUTPUT_PATH, "w") as output_file:
        for section in queries:
            output_file.write(section["explanation"] + "\n")
            for query_info in section["queries"]:
                table_name = query_info["table_name"]
                query = query_info["query"]
                df = pd.read_sql_query(query, conn)
                output_file.write(df.to_string(index=False) + "\n\n")

        # Write all the encodings used
        output_file.write("Encodings used:\n")
        for keyword in SEARCH_TERMS_ENCODINGS.search_terms:
            output_file.write(f"Search term: {keyword}\n")
            for keyword_case in SEARCH_TERMS_ENCODINGS.encodings[keyword].keys():
                output_file.write(f"Keyword case: {keyword_case}\n")
                for encoding_name, encoded_term in SEARCH_TERMS_ENCODINGS.encodings[
                    keyword
                ][keyword_case].items():
                    output_file.write(f"{encoding_name}: {encoded_term}\n")
                output_file.write("\n")

    conn.close()
    conn_leak.close()
