import sqlite3
import pandas as pd
import urllib.parse
import base64
from pathlib import Path

# Connect to the SQLite database
conn = sqlite3.connect(Path("crawl_results.sqlite"))

# Queries for each table
http_requests_query = """
SELECT sv.visit_id,
       sv.site_url,
       hr.request_id,
       hr.url,
       hr.top_level_url,
       hr.referrer,
       hr.headers,
       hr.post_body,
       hr.post_body_raw
FROM site_visits sv
INNER JOIN http_requests hr ON sv.visit_id = hr.visit_id;
"""

javascript_query = """
SELECT sv.visit_id,
       sv.site_url,
       js.value AS js_value
FROM site_visits sv
INNER JOIN javascript js ON sv.visit_id = js.visit_id;
"""

javascript_cookies_query = """
SELECT sv.visit_id,
       sv.site_url,
       jsc.name AS cookie_name,
       jsc.path AS cookie_path,
       jsc.value AS cookie_value
FROM site_visits sv
INNER JOIN javascript_cookies jsc ON sv.visit_id = jsc.visit_id;
"""

# Read the data into separate pandas DataFrames
http_requests_data = pd.read_sql_query(http_requests_query, conn)
javascript_data = pd.read_sql_query(javascript_query, conn)
javascript_cookies_data = pd.read_sql_query(javascript_cookies_query, conn)

# Prepare the search terms
keyword = "JELLYBEANS"
# We could use Ciphey as  paper suggests
# url_encoded_keyword = urllib.parse.quote(keyword) Not useful for our case
base64_encoded_keyword = base64.b64encode(keyword.encode()).decode()
double_base64_encoded_keyword = base64.b64encode(base64_encoded_keyword.encode()).decode()
hex_encoded_keyword = keyword.encode().hex()



search_terms = [keyword, base64_encoded_keyword, double_base64_encoded_keyword, hex_encoded_keyword]

# Function to search for leakage
def search_leakage(data, column, table_name, conn_leak):
    search_term = {
        0: 'original',
        1: 'base64_encoded',
        2: 'double_base64_encoded',
        3: 'hex_encoded'
    }
    for i, term in enumerate(search_terms):
        leakage = data[data[column].str.contains(term, na=False, case=False)]
        if not leakage.empty:
            print(f"Leakage found in {column} with search term: {term}")
            leakage['encoding'] = search_term[i]  # Add the encoding index to the leakage DataFrame
            leakage.to_sql(table_name, conn_leak, if_exists='append', index=False)

# Connect to the SQLite database for leakage data
conn_leak = sqlite3.connect(Path("./leakages/sqlite/leakages_data.sqlite"))

# Create leakage tables
conn_leak.execute("""
CREATE TABLE IF NOT EXISTS http_requests_leakage_data (
    visit_id INTEGER,
    site_url TEXT,
    request_id INTEGER,
    url TEXT,
    top_level_url TEXT,
    referrer TEXT,
    headers TEXT,
    post_body TEXT,
    post_body_raw TEXT,
    encoding TEXT
);
"""
)

conn_leak.execute(
"""
CREATE TABLE IF NOT EXISTS javascript_leakage_data ( 
    visit_id INTEGER,
    site_url TEXT,
    js_value TEXT,
    encoding TEXT
);
"""
)

conn_leak.execute(
"""
CREATE TABLE IF NOT EXISTS javascript_cookies_data ( 
    visit_id INTEGER,
    site_url TEXT,
    cookie_name TEXT,
    cookie_path TEXT,
    cookie_value TEXT,
    encoding TEXT
);
"""
)

conn_leak.commit()

# Search for leakage in relevant columns
columns_to_search_http_requests = [
    "url",
    "referrer",
    "headers",
    "post_body",
    "post_body_raw",
]

columns_to_search_javascript = [
    "js_value",
    ]

columns_to_search_javascript_cookies = [
    "cookie_name",
    "cookie_path",
    "cookie_value",
]

data_dict = {
    "data": [http_requests_data, javascript_data, javascript_cookies_data],
    "columns": [columns_to_search_http_requests, columns_to_search_javascript, columns_to_search_javascript_cookies],
    "table_names": ["http_requests_leakage_data", "javascript_leakage_data", "javascript_cookies_leakage_data"]
}

print("Starting leakage search... \n")

for i in range(3):
    data = data_dict["data"][i]
    columns = data_dict["columns"][i]
    sql_table_name = data_dict["table_names"][i]
    print(f"Starting table {sql_table_name}...\n")
    for j, column in enumerate(columns):
        search_leakage(data, column, sql_table_name, conn_leak)
        print(f"Finished column {column} of table ({i+1})/{3}) ({j+1}/{len(columns)})")


# Write about general crawling results

queries = [
    {
        "explanation": "Sites crawled:",
        "queries": [
            {
                "table_name": "site_visits",
                "query":
                """
                SELECT COUNT(DISTINCT site_url) as sites_crawled
                FROM site_visits;
                """
            }
            ],
    },
    {
        "explanation": "Incomplete visits:",
        "queries": [
            {
                "table_name": "site_visits",
                "query":
                """
                SELECT COUNT(DISTINCT visit_id) as incomplete_visits
                FROM incomplete_visits;
                """
            }
            ],
    },
    {
        "explanation": "Total amount of HTTP Requests captured:",
        "queries": [
            {
                "table_name": "http_requests",
                "query":
                """
                SELECT COUNT(DISTINCT request_id) as http_requests_captured
                FROM http_requests;
                """
            }
            ],
    },
    {
        "explanation": "Total amount of javascripts captured:",
        "queries": [
            {
                "table_name": "javascript",
                "query":
                """
                SELECT COUNT(DISTINCT id) as javascripts_captured
                FROM javascript;
                """
            }
            ],
    },
    {
        "explanation": "Total amount of Cookies captured:",
        "queries": [
            {
                "table_name": "javascript_cookies",
                "query":
                """
                SELECT COUNT(DISTINCT id) as cookies_captured
                FROM javascript_cookies;
                """
            }
            ],
    }
    ]

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
