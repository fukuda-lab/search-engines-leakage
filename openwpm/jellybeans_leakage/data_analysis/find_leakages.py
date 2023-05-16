""" This file is used to search for the actual leakages in the crawled data (HTTP requests, JavaScripts, and Cookies).

If we were to have perfomance issues, we could consider adding the eTLD+1's to the crawl_data database schema and save them at crawling time, so we can make the filtering in the SQL query in stead of relying on pandas dataframe.
"""

import sqlite3
import pandas as pd
import tldextract
import base64
import encodings
from pathlib import Path
from keyword_encoding import get_keyword_encodings
from sqlite import (
    CrawledDataQuery,
    LeakageTableCreationCommand,
    LeakageDataQueries,
    ColumnsToSearch,
    LeakageTableNames,
)

CRAWL_DATA_PATH = Path("sqlite/crawl_results.sqlite")
LEAKAGE_DATA_PATH = Path("leakages/sqlite/leakage_data.sqlite")


def search_leakage(
    table_df: pd.DataFrame, column: str, table_name: str, conn_leak: sqlite3.Connection
) -> None:
    """Evaluates the existence of leakage in a given column among all of the entries of the given table_df."""

    # TODO: Evaluate the perfect criteria, consider adding more suffixes like the Private Domains list used as suffix, from the Public Suffix List (tldextract docs)
    def get_etld_plus_one(url: str) -> str:
        """Returns the eTLD+1 of a given URL."""
        extract = tldextract.extract(url)

        # We get the relevant element (corresponding to the +1) from the subdomain
        subdomain_list = extract.subdomain.split(".")
        subdomain_relevant_element = subdomain_list[-1]

        if subdomain_relevant_element == "":
            return extract.registered_domain

        # We join the relevant element of the subdomain with the registered_domain property
        etld_plus_one = (".").join(
            [subdomain_relevant_element, extract.registered_domain]
        )
        return etld_plus_one

    # TODO: Add more encodings and multiple encodings
    encoding_names = {
        0: "original",
        1: "base16",
        2: "base32",
        3: "base32hex",
        4: "base58",
        5: "base64",
        6: "gz",
        7: "bzip2",
        8: "deflate",
        9: "md5",
        10: "sha1",
        11: "sha224",
        12: "sha256",
        13: "sha384",
        14: "sha512",
        15: "sha3_224",
        16: "sha3_256",
        17: "sha3_384",
        18: "sha3_512",
        19: "blake2s",
        20: "blake2b",
        21: "ripemd_128",
        22: "ripemd_160",
        23: "ripemd_256",
        24: "ripemd_320",
        25: "crc16",
        26: "crc32",
        27: "adler32",
        28: "rot13",
    }

    # Traverse all encodings
    for i, term in enumerate(search_terms):
        # In the case of http_requests, the leakage criteria is eTLD+1 matching as in the paper (see Section 4.1)
        # So we must filter the table_df to only contain the requests made to third parties
        if table_name == LeakageTableNames.HTTP_REQUESTS:
            table_df["top_level_url_etld_plus_one"] = table_df["top_level_url"].apply(
                get_etld_plus_one
            )
            table_df["request_url_etld_plus_one"] = table_df["url"].apply(
                get_etld_plus_one
            )

            # Get a series of boolean values that indicate whether the request is to a third party
            requests_to_third_parties = (
                table_df["top_level_url_etld_plus_one"]
                != table_df["request_url_etld_plus_one"]
            )
            # Get another series of boolean values to indicate whether the top_level_url_etld_plus_one is not a substring of the request_url_etld_plus_one
            top_level_domain_not_in_request_url_domain = table_df.apply(
                lambda row: row["top_level_url_etld_plus_one"]
                not in row["request_url_etld_plus_one"],
                axis=1,  # Argument to indicate that we want to apply the function to rows in stead of columns
            )

            # Join the two series of boolean values with a logical AND operation to get the final series of boolean values including the two conditions
            requests_to_third_parties = (
                requests_to_third_parties & top_level_domain_not_in_request_url_domain
            )

            # Filter dataframe based on condition (using the series as a mask)
            table_df = table_df[requests_to_third_parties]

        # Get a series of boolean True values for the rows that contain the search term with the actual evaluated encoding
        leakages_index_series: pd.Series = table_df[column].str.contains(
            term, na=False, case=False
        )
        leakages = table_df[leakages_index_series]
        if not leakages.empty:
            print(f"Leakages found in {column} with search term: {term}")
            # Add the encoding and site_url to the leakages DataFrame
            leakages["encoding"] = encoding_names[i]
            leakages["site_url"] = table_df["site_url"]
            leakages.to_sql(table_name, conn_leak, if_exists="append", index=False)


# Connect to the SQLite database
conn = sqlite3.connect(CRAWL_DATA_PATH)

# Read the data into separate pandas DataFrames
http_requests_data = pd.read_sql_query(CrawledDataQuery.HTTP_REQUESTS, conn)
javascript_data = pd.read_sql_query(CrawledDataQuery.JS, conn)
javascript_cookies_data = pd.read_sql_query(CrawledDataQuery.COOKIES, conn)

# Prepare the search terms
keyword = "JELLYBEANS"
# We could use Ciphey as  paper suggests


# PREVIOUSLY USED ENCODINGS
# url_encoded_keyword = urllib.parse.quote(keyword) Not useful for our case
# base64_encoded_keyword = base64.b64encode(keyword.encode()).decode()
# double_base64_encoded_keyword = base64.b64encode(
#     base64_encoded_keyword.encode()
# ).decode()
# hex_encoded_keyword = keyword.encode().hex()
# search_terms = [
#     keyword,
#     base64_encoded_keyword,
#     double_base64_encoded_keyword,
#     hex_encoded_keyword,
# ]

# New encodings:
search_terms = get_keyword_encodings(keyword)


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
