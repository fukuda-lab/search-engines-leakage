import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("sqlite/leakages_data.sqlite")

# List of queries and their explanations
queries = [
    {
        "explanation": "1. Total number of leakages found in each table:",
        "queries": [
            {
                "table_name": "http_requests_leakage_data",
                "query": "SELECT COUNT(*) as num_leakages FROM http_requests_leakage_data;",
            },
            {
                "table_name": "javascript_leakage_data",
                "query": "SELECT COUNT(*) as num_leakages FROM javascript_leakage_data;",
            },
            {
                "table_name": "javascript_cookies_leakage_data",
                "query": "SELECT COUNT(*) as num_leakages FROM javascript_cookies_leakage_data;",
            },
        ],
    },
{
        "explanation": "2. Total leakages per table breakdown:",
        "queries": [
            {
                "table_name": "http_requests_leakage_data",
                "query": """
                SELECT site_url, COUNT(*) as total_leakages, COUNT(url) as url_leakages, COUNT(referrer) as referrer_leakages, COUNT(headers) as headers_leakages, COUNT(post_body) as post_body_leakages, COUNT(post_body_raw) as post_body_raw_leakages
                FROM http_requests_leakage_data
                GROUP BY site_url
                ORDER BY total_leakages DESC;
                """,
            },
            {
                "table_name": "javascript_leakage_data",
                "query": """
                SELECT site_url, COUNT(js_value) as js_value_leakages, count(*) as total_leakages
                FROM javascript_leakage_data
                GROUP BY site_url
                ORDER BY js_value_leakages DESC;
                """,
            },
            {
                "table_name": "javascript_cookies_leakage_data",
                "query": """
                SELECT site_url, count(*) as total_leakages, count(cookie_name) as cookie_name_leakages, count(cookie_path) as cookie_path_leakages, count(cookie_value) as cookie_value_leakages
                FROM javascript_cookies_leakage_data
                GROUP BY site_url
                ORDER BY total_leakages DESC;
                """,
            },
        ],
    },
    {
        "explanation": "3. Number of leakages per encoding type in each table:",
        "queries": [
            {
                "table_name": "http_requests_leakage_data",
                "query": """
                SELECT encoding, COUNT(*) as num_leakages
                FROM http_requests_leakage_data
                GROUP BY encoding
                ORDER BY num_leakages DESC;
                """,
            },
            {
                "table_name": "javascript_leakage_data",
                "query": """
                SELECT encoding, COUNT(*) as num_leakages
                FROM javascript_leakage_data
                GROUP BY encoding
                ORDER BY num_leakages DESC;
                """,
            },
            {
                "table_name": "javascript_cookies_leakage_data",
                "query": """
                SELECT encoding, COUNT(*) as num_leakages
                FROM javascript_cookies_leakage_data
                GROUP BY encoding
                ORDER BY num_leakages DESC;
                """,
            },
        ],
    },
]

# Execute the queries and write the results to an output file
with open("results/leakages_overall_metrics.txt", "w") as output_file:
    for section in queries:
        output_file.write(section["explanation"] + "\n")
        for query_info in section["queries"]:
            table_name = query_info["table_name"]
            query = query_info["query"]
            df = pd.read_sql_query(query, conn)
            output_file.write(f"{table_name}:\n")
            output_file.write(df.to_string(index=False) + "\n\n")