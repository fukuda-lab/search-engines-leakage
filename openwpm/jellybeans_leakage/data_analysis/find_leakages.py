""" This file is used to search for the actual leakages in the crawled data (HTTP requests, JavaScripts, and Cookies).
If we were to have perfomance issues, we could consider adding the eTLD+1's to the crawl_data database schema and save them at crawling time, so we can make the filtering in the SQL query in stead of relying on pandas dataframe.
"""

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
    table_df: pd.DataFrame,
    columns: list,
    table_name: str,
    conn_leak: sqlite3.Connection,
) -> None:
    """Evaluates the existence of leakage in a given column among all of the entries of the given table_df.
    The criteria used is Second-Level Domain difference.
    Keep in mind that, due to the use of already_added_elements (which is used in order to not have duplicates in our leakages table),
    this function does not detect all the leakages, but only the first one found for each original_id (if any).
    """

    df = table_df.copy()
    already_added_elements = pd.Series([False] * len(table_df), index=df.index)

    # (1) We will use DataFrame and concat with every new group of leakages after each column,
    # because it is faster than appending to a list of DataFrames and then concatenating them.
    # However, this is more memory heavy than the list approach, so we will have to be careful with the amount of data we are handling.
    resulting_leakages = pd.DataFrame()

    # Filter the table_df to only contain the requests made to third parties

    if table_name == LeakageTableNames.HTTP_REQUESTS:
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

    elif table_name == LeakageTableNames.JS:
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

    elif table_name == LeakageTableNames.COOKIES:
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

    # Traverse all search_terms (just one for now)
    for keyword in SEARCH_TERMS_ENCODINGS.search_terms:
        # Traverse original and lowercase
        for keyword_case in SEARCH_TERMS_ENCODINGS.encodings[keyword].keys():
            # Traverse all encodings for the current search term and case
            for encoding_name, encoded_term in SEARCH_TERMS_ENCODINGS.encodings[
                keyword
            ][keyword_case].items():
                for i, column in enumerate(columns):
                    # Get a series of boolean True values to filter only for the rows that contain the search term with the actual evaluated encoding
                    leakages_indexes = pd.Series(
                        df[column].str.contains(
                            encoded_term,
                            na=False,
                            case=True,  # We are handling the casing in the SEARCH_TERMS_ENCODINGS, so we set this to True to avoid duplicates
                        ),
                        index=df.index,
                    )
                    # We must also filter out the rows that have already been added to the leakages table, in order to not include duplicates
                    complete_mask = pd.Series(
                        leakages_indexes & ~already_added_elements, index=df.index
                    )
                    # We update the already_added_elements series to include the new found leakages
                    already_added_elements = pd.Series(
                        already_added_elements | leakages_indexes, index=df.index
                    )

                    leakages = df[complete_mask].copy()
                    if not leakages.empty:
                        print(
                            f"Leakages found in column {column} with search"
                            f" encoded_term: {encoded_term}"
                        )
                        # Add the encoding and site_url to the leakages DataFrame
                        if keyword_case == "lowercase":
                            encoding_name = encoding_name + "_lowercase"

                        # Pandas can confuse wether to make this assignment to a copy or to the original leakages table, so better to specify it with .loc
                        leakages.loc[:, "encoding"] = encoding_name
                        leakages.loc[:, "original_id"] = df.loc[
                            complete_mask, "original_id"
                        ]

                    # (1) Here we can use a list, append leakages and concat at the end (in stead of a DataFrame and concat here directly)
                    resulting_leakages = pd.concat(
                        [resulting_leakages, leakages],
                        ignore_index=True,  # Not sure if ignore_index should be True
                    )
    resulting_leakages.to_sql(table_name, conn_leak, if_exists="append", index=False)
    print(f"Finished table {table_name}")


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
        search_leakage(table, columns, table_name, conn_leak)

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
