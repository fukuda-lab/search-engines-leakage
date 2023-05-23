""" This file is used to obtain general metrics about the leakages found in the crawled data (HTTP requests, JavaScripts, and Cookies) by the find_leakages.py script. The metrics are written to a text file in the results folder. """

import sqlite3
import pandas as pd
from pathlib import Path

# We are running this script standing in a parent directory (leakage_processing.py file)
from data_analysis.leakages.sqlite import GeneralAnalysis


def generate_general_metrics(
    LEAKAGE_DATA_PATH: Path, LEAKAGE_GENERAL_OUTPUT_PATH: Path
):
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
