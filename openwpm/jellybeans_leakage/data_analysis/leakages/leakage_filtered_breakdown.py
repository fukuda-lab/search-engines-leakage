import os
import sqlite3
import json
from collections import defaultdict

# Connect to the SQLite database
conn = sqlite3.connect("sqlite/leakages_data.sqlite")

# Define the queries for each table
http_requests_query = """
SELECT site_url, url, top_level_url, referrer, headers, post_body, post_body_raw, encoding
FROM http_requests_leakage_data;
"""

javascript_query = """
SELECT site_url, js_value, encoding
FROM javascript_leakage_data;
"""

javascript_cookies_query = """
SELECT site_url, cookie_name, cookie_path, cookie_value, encoding
FROM javascript_cookies_leakage_data;
"""

# Execute the queries and fetch the results
http_requests_leakage = conn.execute(http_requests_query).fetchall()
javascript_leakage = conn.execute(javascript_query).fetchall()
javascript_cookies_leakage = conn.execute(javascript_cookies_query).fetchall()

# Organize the leakage data by site_url
leakage_details = defaultdict(lambda: defaultdict(list))

search_terms = ["JELLYBEANS"]

for row in http_requests_leakage:
    site_url, url, top_level_url, referrer, headers, post_body, post_body_raw, encoding = row
    leakage = {"url": url, "encoding": encoding}
    for term in search_terms:
        if term.lower() in (top_level_url or "").lower():
            leakage["top_level_url"] = top_level_url
        if term.lower() in (referrer or "").lower():
            leakage["referrer"] = referrer
        if term.lower() in (headers or "").lower():
            leakage["headers"] = headers
        if term.lower() in (post_body or "").lower():
            leakage["post_body"] = post_body
        if term.lower() in (post_body_raw or "").lower():
            leakage["post_body_raw"] = post_body_raw
    leakage_details[site_url]["http_requests"].append(leakage)

for row in javascript_leakage:
    site_url, js_value, encoding = row
    leakage = {"encoding": encoding}
    for term in search_terms:
        if term.lower() in (js_value or "").lower():
            leakage["js_value"] = js_value
    leakage_details[site_url]["javascript"].append(leakage)

for row in javascript_cookies_leakage:
    site_url, cookie_name, cookie_path, cookie_value, encoding = row
    leakage = {"encoding": encoding}
    for term in search_terms:
        leakage["cookie_name"] = cookie_name
        leakage["cookie_path"] = cookie_path
        leakage["cookie_value"] = cookie_value
    leakage_details[site_url]["javascript_cookies"].append(leakage)

# Save the leakage details in JSON format
with open("leakage_filtered_breakdown.json", "w") as outfile:
    json.dump(leakage_details, outfile, indent=4, sort_keys=True)

# Close the database connection
conn.close()