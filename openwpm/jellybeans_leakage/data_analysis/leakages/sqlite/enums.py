class GeneralAnalysis:
    QUERIES = [
        {
            "explanation": "1. Total number of leakages found in each table:",
            "queries": [
                {
                    "table_name": "http_requests_leakage_data",
                    "query": (
                        "SELECT COUNT(*) as num_leakages FROM"
                        " http_requests_leakage_data;"
                    ),
                },
                {
                    "table_name": "javascript_leakage_data",
                    "query": (
                        "SELECT COUNT(*) as num_leakages FROM javascript_leakage_data;"
                    ),
                },
                {
                    "table_name": "javascript_cookies_leakage_data",
                    "query": (
                        "SELECT COUNT(*) as num_leakages FROM"
                        " javascript_cookies_leakage_data;"
                    ),
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
                SELECT site_url, COUNT(value) as js_value_leakages, count(*) as total_leakages
                FROM javascript_leakage_data
                GROUP BY site_url
                ORDER BY js_value_leakages DESC;
                """,
                },
                {
                    "table_name": "javascript_cookies_leakage_data",
                    "query": """
                SELECT site_url, count(*) as total_leakages, count(name) as cookie_name_leakages, count(path) as cookie_path_leakages, count(value) as cookie_value_leakages
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


# Queries to get the details of each leakages table
class LeakagesDetailsQueryBySiteURL:
    # TODO: 1. Add a column that is only the domain name of the search engine (e.g. google.com) so we can group by that and decouple from the search term
    #       2. Refactor this class
    def __init__(self, site_url) -> None:
        self.site_url = site_url
        self.HTTPRequests = self._get_http_leakages_query_by_url()
        self.JS = self._get_javascript_leakages_query_by_url()
        self.COOKIES = self._get_cookies_leakages_query_by_url()

    def _get_http_leakages_query_by_url(self):
        return (
            "SELECT  url, "
            "        top_level_url, "
            "        referrer, "
            "        headers, "
            "        post_body, "
            "        post_body_raw, "
            "        encoding, "
            "        is_third_party_channel, "
            "        is_third_party_to_top_window, "
            "        top_level_url_second_level_domain, "
            "        request_url_second_level_domain "
            "FROM http_requests_leakage_data "
            f"WHERE site_url = '{self.site_url}'; "
        )

    def _get_javascript_leakages_query_by_url(self):
        return (
            "SELECT value, "
            "        func_name, "
            "        script_url, "
            "        document_url, "
            "        top_level_url, "
            "        arguments, "
            "        encoding "
            "FROM javascript_leakage_data "
            f"WHERE site_url = '{self.site_url}';"
        )

    def _get_cookies_leakages_query_by_url(self):
        return (
            "SELECT name, "
            "        path, "
            "        value, "
            "        same_site, "
            "        first_party_domain, "
            "        host, "
            "        is_secure, "
            "        encoding "
            "FROM javascript_cookies_leakage_data "
            f"WHERE site_url = '{self.site_url}';"
        )
