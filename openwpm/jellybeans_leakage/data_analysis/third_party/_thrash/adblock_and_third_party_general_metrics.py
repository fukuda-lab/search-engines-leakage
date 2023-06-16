""" File to attach the database with the adblock lists matches from both python adblock repository and javascript brave repository with the crawled-third party filtered data database """
from pathlib import Path
import sqlite3
import pandas as pd


def join_databases(THIRD_PARTY_DATA_PATH, ADBLOCK_DATA_PATH):
    # Connect to the first database file
    conn = sqlite3.connect(THIRD_PARTY_DATA_PATH)

    # Create a cursor object
    cursor = conn.cursor()

    # Attach the second database file
    cursor.execute(f"ATTACH DATABASE '{ADBLOCK_DATA_PATH}' AS adblock")

    query_http = """
        SELECT  t1.original_id as original_id,
                t1.site_url as site_url,
                t1.url as url,
                t1.top_level_url as top_level_url,
                t2.easylist as easylist,
                t2.easyprivacy as easyprivacy,
                t2.exceptionlist as exceptionlist,
                easylist + easyprivacy + exceptionlist as total 
        FROM http_requests_third_party AS t1
        INNER JOIN adblock.http_requests_abp AS t2
        ON t1.original_id = t2.id
    """
    query_js = """
        SELECT  t1.original_id as original_id,
                t1.site_url as site_url,
                t1.script_url as script_url,
                t1.document_url as document_url,
                t1.top_level_url as top_level_url,
                t2.easylist as easylist,
                t2.easyprivacy as easyprivacy,
                t2.exceptionlist as exceptionlist,
                easylist + easyprivacy + exceptionlist as total 
        FROM javascript_third_party AS t1
        INNER JOIN adblock.javascripts_abp AS t2
        ON t1.original_id = t2.id
    """

    # Execute the query, fetch the results and save them in a variable
    cursor.execute(query_http)
    results_http_requests = cursor.fetchall()

    cursor.execute(query_js)
    results_javascripts = cursor.fetchall()

    # Clean up
    cursor.close()
    conn.close()

    return results_http_requests, results_javascripts


def get_general_metrics(results_http_requests, results_javascripts, OUTPUT_PATH):
    # Convert the results to pandas DataFrame for easier data manipulation
    df_http_requests = pd.DataFrame(
        results_http_requests,
        columns=[
            "original_id",
            "site_url",
            "url",
            "top_level_url",
            "easylist",
            "easyprivacy",
            "exceptionlist",
            "total",
        ],
    )
    df_javascripts = pd.DataFrame(
        results_javascripts,
        columns=[
            "original_id",
            "site_url",
            "script_url",
            "document_url",
            "top_level_url",
            "easylist",
            "easyprivacy",
            "exceptionlist",
            "total",
        ],
    )

    # Group by 'site_url' and sum the rest of the columns
    grouped_http_requests = (
        df_http_requests.groupby("site_url")[
            ["easylist", "easyprivacy", "exceptionlist", "total"]
        ]
        .sum(numeric_only=True)
        .sort_values(by="total", ascending=False)
    )
    grouped_javascripts = (
        df_javascripts.groupby("site_url")[
            ["easylist", "easyprivacy", "exceptionlist", "total"]
        ]
        .sum(numeric_only=True)
        .sort_values(by="total", ascending=False)
    )

    # Calculate the total sum for each DataFrame
    total_http_requests = df_http_requests[
        ["easylist", "easyprivacy", "exceptionlist"]
    ].sum()
    total_javascripts = df_javascripts[
        ["easylist", "easyprivacy", "exceptionlist"]
    ].sum()

    with open(OUTPUT_PATH, "w") as f:
        f.write("Total number of matches for each ruleset in each table\n")
        f.write("http_requests_abp:\n")
        f.write(" easylist  easyprivacy  exceptionlist\n")
        f.write(
            f"  {total_http_requests['easylist']}     "
            f"    {total_http_requests['easyprivacy']}           "
            f" {total_http_requests['exceptionlist']}\n\n"
        )

        f.write("javascripts_abp:\n")
        f.write(" easylist  easyprivacy  exceptionlist\n")
        f.write(
            f"  {total_javascripts['easylist']}        "
            f" {total_javascripts['easyprivacy']}           "
            f" {total_javascripts['exceptionlist']}\n\n"
        )

        f.write("Number of matches for each ruleset for each site_url in each table\n")
        f.write("http_requests_abp:\n")
        f.write(grouped_http_requests.to_string() + "\n\n")
        f.write("javascripts_abp:\n")
        f.write(grouped_javascripts.to_string() + "\n")

    print(f"General metrics for saved in {OUTPUT_PATH}")


# Path to the db with the crawled data filtered to third parties only
THIRD_PARTY_DATA_PATH = Path("sqlite/[vpn_chile]10_crawls_third_party.sqlite")

# Path to the db with python adblock's library matches and output file name
PYTHON_ADBLOCK_DATA_PATH = Path("python/sqlite/[vpn_chile]10_crawls_adblock.sqlite")
PYTHON_OUTPUT_PATH = Path("results/[vpn_chile]python_general_metrics.txt")

# Path to the db with javascript adblock's library matches and output file name
JS_ADBLOCK_DATA_PATH = Path("JS/sqlite/[vpn_chile]10_crawls_adblock.sqlite")
JS_OUTPUT_PATH = Path("results/[vpn_chile]js_general_metrics.txt")

# We run for python first
python_results_http_requests, python_results_javascripts = join_databases(
    THIRD_PARTY_DATA_PATH, PYTHON_ADBLOCK_DATA_PATH
)

get_general_metrics(
    python_results_http_requests,
    python_results_javascripts,
    PYTHON_OUTPUT_PATH,
)

# Then we run for javascript
js_results_http_requests, js_results_javascripts = join_databases(
    THIRD_PARTY_DATA_PATH, JS_ADBLOCK_DATA_PATH
)

get_general_metrics(
    js_results_http_requests,
    js_results_javascripts,
    JS_OUTPUT_PATH,
)
