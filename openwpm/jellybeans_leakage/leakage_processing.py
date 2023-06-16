import os
from pathlib import Path
from data_analysis.find_leakages import find_leakages
from data_analysis.leakages.generate_general_metrics import generate_general_metrics
from data_analysis.leakages.generate_detail_json import generate_leakage_details_json

# Modify this one to change the source of the crawled data
source = input(
    "Enter the source of the crawled data (e.g. [tokyo], [vpn_chile], [vpn_czech]): "
)
if source not in ["[tokyo]", "[vpn_chile]", "[vpn_czech]"]:
    print("Invalid source.")
    exit(1)

CRAWL_DATA_PATH = Path(f"data_analysis/sqlite/{source}10_crawls_results.sqlite")

LEAKAGE_DATA_PATH = Path(f"data_analysis/leakages/sqlite/{source}leakage_data.sqlite")
OVERALL_OUTPUT_PATH = Path(
    f"data_analysis/leakages/results/{source}crawl_data_metrics.txt"
)

GENERAL_OUTPUT_PATH = Path(
    f"data_analysis/leakages/results/{source}leakage_overall_metrics.txt"
)

DETAILS_OUTPUT_PATH = Path(
    f"data_analysis/leakages/results/{source}leakages_by_type_and_site_url.json"
)

# Print the data to perform the analysis to (CRAWL_DATA_PATH)
print(f"----------- Performing leakage analysis to {CRAWL_DATA_PATH}... -----------")
# Perform the leakage analysis
find_leakages(CRAWL_DATA_PATH, LEAKAGE_DATA_PATH, OVERALL_OUTPUT_PATH)

# Obtain general metrics about the leakages found in the crawled data (HTTP requests, JavaScripts, and Cookies)
print(f"------- Generating general metrics to {GENERAL_OUTPUT_PATH}... -------")
generate_general_metrics(LEAKAGE_DATA_PATH, GENERAL_OUTPUT_PATH)

# Obtain the details of the leakages found in the crawled data (HTTP requests, JavaScripts, and Cookies)
print(
    f"------------- Generating leakage details to {DETAILS_OUTPUT_PATH}..."
    " -------------"
)
generate_leakage_details_json(LEAKAGE_DATA_PATH, DETAILS_OUTPUT_PATH)
