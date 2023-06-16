from adblockparser import AdblockRules
import json
import time
import pandas as pd
import sqlite3
from pathlib import Path
from utils import MatchingFunctions

from sqlite.enums import CrawledDataQueryForABP, CreateABPTablesCommands

# Start timer
start_time = time.time()
print("Starting rule parsing...")

# ------------------ Functions ------------------


def parse_list_file(filename):
    with open(filename, "r") as f:
        raw_rules = f.readlines()
    rules = AdblockRules(raw_rules)
    print(f"Parsed {filename}")
    return rules


def json_to_dictionary(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def match_http_requests_and_filter(data: pd.DataFrame, http_matching_function):
    """Function to get the matching info of all the http_requests with different rulesets"""
    print("Applying rulesets to http_requests...")
    http_requests_df = data.copy()

    # We apply the ruleset to the data
    http_requests_df[["easylist", "easyprivacy", "exceptionlist"]] = http_requests_df[
        ["url", "id", "top_level_url"]
    ].apply(http_matching_function, axis=1, result_type="expand")

    http_requests_df = http_requests_df[
        (http_requests_df["easylist"] == 1)
        | (http_requests_df["easyprivacy"] == 1)
        | (http_requests_df["exceptionlist"] == 1)
    ]

    print("All rulesets applied for http_requests \n")
    return http_requests_df


def match_javascripts_and_filter(data: pd.DataFrame, javascript_matching_function):
    """Function to get the matching info of all the javascripts with different rulesets"""
    print("Applying rulesets to javascripts...")
    javascripts_df = data.copy()

    # We apply the ruleset to the data
    javascripts_df[["easylist", "easyprivacy", "exceptionlist"]] = javascripts_df[
        ["script_url", "id", "top_level_url"]
    ].apply(javascript_matching_function, axis=1, result_type="expand")

    javascripts_df = javascripts_df[
        (javascripts_df["easylist"] == 1)
        | (javascripts_df["easyprivacy"] == 1)
        | (javascripts_df["exceptionlist"] == 1)
    ]

    print("All rulesets applied for javascripts \n")
    return javascripts_df


def run_matching_and_save(CRAWL_DATA_PATH, OUTPUT_PATH):
    """Global function to connect to the database and make the corresponding calls to get the matching results"""

    # We parse the rulesets
    ruleset_dict = {
        "easylist": parse_list_file("easylist.txt"),
        "easyprivacy": parse_list_file("easyprivacy.txt"),
        "exception": parse_list_file("exceptionrules.txt"),
    }

    # We connect to the databases
    crawl_conn = sqlite3.connect(CRAWL_DATA_PATH)
    abp_conn = sqlite3.connect(OUTPUT_PATH)

    # We create the tables for the output
    abp_conn.execute(CreateABPTablesCommands.HTTP_REQUESTS)
    abp_conn.execute(CreateABPTablesCommands.JS)

    # We get the data from the database
    http_requests_data = pd.read_sql_query(
        CrawledDataQueryForABP.HTTP_REQUESTS, crawl_conn
    )
    javascript_data = pd.read_sql_query(CrawledDataQueryForABP.JS, crawl_conn)

    # We get the matching functions (we need to pass the length of the data to measure the progress)
    matching_functions = MatchingFunctions(
        ruleset_dict, len(http_requests_data), len(javascript_data)
    )

    # We get the matching results
    matched_http_requests = match_http_requests_and_filter(
        http_requests_data, matching_functions.get_http_request_matches
    )
    matched_javascripts = match_javascripts_and_filter(
        javascript_data, matching_functions.get_javascript_matches
    )

    # We save the results
    matched_http_requests.to_sql(
        "http_requests_abp", abp_conn, if_exists="append", index=False
    )
    matched_javascripts.to_sql(
        "javascripts_abp", abp_conn, if_exists="append", index=False
    )

    # We close the connections
    crawl_conn.close()
    abp_conn.close()


# ------------------ Run ------------------

CRAWL_DATA_PATH = Path("../../sqlite/[vpn_czech]10_crawls_results.sqlite")
OUTPUT_PATH = Path("sqlite/[vpn_czech]10_crawls_adblock.sqlite")

run_matching_and_save(CRAWL_DATA_PATH, OUTPUT_PATH)

# Print the amount of seconds it took to run the script
print("Finished in %s seconds" % (time.time() - start_time))
