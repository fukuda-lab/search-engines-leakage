""" This file is used to obtain general metrics about the leakages found in the crawled data (HTTP requests, JavaScripts, and Cookies) by the find_leakages.py script. The metrics are written to a text file in the results folder. """

import sqlite3
import pandas as pd
from pathlib import Path

from sqlite import GeneralAnalysis

LEAKAGE_DATA_PATH = Path("leakages/sqlite/leakage_data.sqlite")

# LEAKAGE_GENERAL_OUTPUT_DATA_PATH = "results/leakage_overall_metrics.txt"
LEAKAGE_GENERAL_OUTPUT_PATH = Path("leakages/results/leakage_overall_metrics.txt")

# Connect to the SQLite database
conn = sqlite3.connect(LEAKAGE_DATA_PATH)

# List of queries and their explanations
queries = GeneralAnalysis.QUERIES

# Execute the queries and write the results to an output file
with open(LEAKAGE_GENERAL_OUTPUT_PATH, "w+") as output_file:
    for section in queries:
        output_file.write(section["explanation"] + "\n")
        for query_info in section["queries"]:
            table_name = query_info["table_name"]
            query = query_info["query"]
            df = pd.read_sql_query(query, conn)
            output_file.write(f"{table_name}:\n")
            output_file.write(df.to_string(index=False) + "\n\n")
