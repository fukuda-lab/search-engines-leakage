import sqlite3
import re


# Connect to the SQLite database
conn = sqlite3.connect("datadir/tranco_100.sqlite")

# Query the amount of requests made by each browser
sites_query = """
SELECT http_requests.browser_id, COUNT(*) AS num_requests
FROM http_requests
GROUP BY browser_id
ORDER BY num_requests DESC
"""
requests = conn.execute(sites_query).fetchall()


# Print the results
print("Browser (crawl) requests:")
for request in requests:
    print(f"Browser_id={request[0]}: {request[1]}")


# Query the amount of responses received by each browser
sites_query = """
SELECT http_responses.browser_id, COUNT(*) AS num_responses
FROM http_responses
GROUP BY browser_id
ORDER BY num_responses DESC
"""
responses = conn.execute(sites_query).fetchall()


# Print the results
print("Browser (crawl) responses:")
for responses in responses:
    print(f"Browser_id={responses[0]}: {responses[1]}")

# For each site_url, get the difference between the requests made by the browser
# without blocklist and the ones by the browser with blocklist. This is an estimate
# of the requests blocked for that site_url by using the blocklist.
sites_query = """
SELECT
  without_blocklist.site_url,
  COUNT(DISTINCT without_blocklist_requests.id) AS requests_without_blocklist,
  COUNT(DISTINCT with_blocklist_requests.id) AS requests_with_blocklist,
  COUNT(DISTINCT without_blocklist_requests.id) - COUNT(DISTINCT with_blocklist_requests.id) AS blocked_requests
FROM
  site_visits AS without_blocklist
  INNER JOIN http_requests AS without_blocklist_requests
    ON without_blocklist.visit_id = without_blocklist_requests.visit_id
    AND without_blocklist.browser_id = without_blocklist_requests.browser_id
  LEFT JOIN site_visits AS with_blocklist
    ON without_blocklist.site_url = with_blocklist.site_url
    AND with_blocklist.browser_id = 3251089431
  LEFT JOIN http_requests AS with_blocklist_requests
    ON with_blocklist.visit_id = with_blocklist_requests.visit_id
    AND with_blocklist.browser_id = with_blocklist_requests.browser_id
    AND with_blocklist_requests.url NOT IN (
      SELECT url
      FROM http_requests
      WHERE browser_id = 1502965085
    )
WHERE
  without_blocklist.browser_id = 1502965085
GROUP BY
  without_blocklist.site_url
ORDER BY blocked_requests DESC
LIMIT 20
"""
requests_per_site_url = conn.execute(sites_query).fetchall()

# Print the results
print("Estimated number of requests blocked by blocklist:")
for site_url in requests_per_site_url:
    print(
        f"{site_url[0]}: without_blocklist = {site_url[1]} | with_blocklist = {site_url[2]} | est_blocked_requests = {site_url[3]}"
    )

# without blocklist id = 1502965085
# with blocklist task 1835721461 id = 3251089431

# GET REGEXP COINCIDENCES OF REQUESTS MADE BY CRAWLING WITHOUT BLOCKLIST

# Get EasyList entries and convert them to RegExp
with open("easylist_general_block.txt", "r") as f:
    entries = f.read().splitlines()

entry = "||example.com^"
regex = re.compile(r"^https?://([^/]+\.)?" + re.escape(entry[2:-1]) + r"/")

regexes = []
for entry in entries:
    if entry.startswith("||"):
        regex = re.compile(r"^https?://([^/]+\.)?" + re.escape(entry[2:-1]) + r"/")
        regexes.append(regex)
    elif entry.startswith("|"):
        regex = re.compile(re.escape(entry[1:]))
        regexes.append(regex)
    elif entry.startswith("/"):
        regex = re.compile(entry[1:-1])
        regexes.append(regex)


# Use expressions to match with requests entries
conn = sqlite3.connect("datadir/tranco_100.sqlite")
c = conn.cursor()


# Just as a tool to analyze the differences, we want to get relevant amount of blocks
asc_coincidences = []
max_dif = 0


# Open a file to write the results
with open("output_tranco100_regexes.txt", "w") as f:
    for regex in regexes:
        # Should I use top_level_url in stead of url?
        # add the browser_id of the one without blocklist
        query = "SELECT COUNT(*) FROM http_requests WHERE url REGEXP ? AND browser_id="
        c.execute(query, (regex.pattern,))
        result_without_blocklist = c.fetchone()

        # add the browser_id of the one with blocklist
        query = "SELECT COUNT(*) FROM http_requests WHERE url REGEXP ? AND browser_id="
        c.execute(query, (regex.pattern,))
        result_with_blocklist = c.fetchone()

        difference = result_without_blocklist - result_with_blocklist

        if difference > max_dif:
            print(f"Estimated blocked requests for {regex.pattern}: {difference}")

            actual = (
                regex.pattern,
                result_without_blocklist,
                result_with_blocklist,
                difference,
            )
            asc_coincidences.append(actual)
            max_dif = difference
            f.write(
                f"{len(asc_coincidences)}) {regex.pattern}: {result_without_blocklist} - {result_with_blocklist} = {difference}\n"
            )

conn.close()
