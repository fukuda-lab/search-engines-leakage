""" File to store SQL strings used in leakage finding """

from enum import StrEnum, Enum


class CrawledDataQuery(StrEnum):
    """Enum class to store SQL queries to retrieve crawled data"""

    HTTP_REQUESTS = """
    SELECT sv.visit_id,
        sv.site_url,
        hr.request_id,
        hr.url,
        hr.top_level_url,
        hr.method,
        hr.referrer,
        hr.headers,
        hr.post_body,
        hr.post_body_raw,
        hr.triggering_origin,
        hr.loading_origin,
        hr.loading_href,
        hr.is_third_party_channel,
        hr.is_third_party_to_top_window,
        hr.is_XHR,
        hr.id as original_id 
    FROM site_visits sv
    INNER JOIN http_requests hr ON sv.visit_id = hr.visit_id;
    """

    JS = """
    SELECT sv.visit_id,
        sv.site_url,
        js.value,
        js.func_name,
        js.script_url,
        js.document_url,
        js.top_level_url,
        js.arguments,
        js.id as original_id 
    FROM site_visits sv
    INNER JOIN javascript js ON sv.visit_id = js.visit_id;
    """

    COOKIES = """
    SELECT sv.visit_id,
        sv.site_url,
        jsc.record_type,
        jsc.change_cause,
        jsc.expiry,
        jsc.host,
        jsc.is_secure,
        jsc.name,
        jsc.path,
        jsc.value,
        jsc.same_site,
        jsc.first_party_domain,
        jsc.id as original_id 
    FROM site_visits sv
    INNER JOIN javascript_cookies jsc ON sv.visit_id = jsc.visit_id;
    """


class LeakageTableNames(StrEnum):
    """Enum class to store the names of the tables with leakage data.
    Make sure to have the same names here and in the LeakageTableCreationCommand
    """

    HTTP_REQUESTS = "http_requests_leakage_data"
    JS = "javascript_leakage_data"
    COOKIES = "javascript_cookies_leakage_data"


class LeakageDropTableCommand(StrEnum):
    HTTP_REQUESTS = """
    DROP TABLE IF EXISTS http_requests_leakage_data;
    """

    JS = """
    DROP TABLE IF EXISTS javascript_leakage_data;
    """

    COOKIES = """
    DROP TABLE IF EXISTS javascript_cookies_leakage_data;
    """


class LeakageTableCreationCommand(StrEnum):
    """Enum class to store SQL commands to create leakage tables"""

    HTTP_REQUESTS = """
    CREATE TABLE IF NOT EXISTS http_requests_leakage_data ( 
        original_id INTEGER PRIMARY KEY,
        visit_id INTEGER,
        site_url TEXT,
        request_id INTEGER,
        url TEXT,
        top_level_url TEXT,
        method TEXT NOT NULL,
        referrer TEXT,
        headers TEXT,
        post_body TEXT,
        post_body_raw TEXT,
        triggering_origin TEXT,
        loading_origin TEXT,
        loading_href TEXT,
        is_third_party_channel INTEGER,
        is_third_party_to_top_window INTEGER,
        is_XHR INTEGER,
        encoding TEXT,
        top_level_url_second_level_domain TEXT,
        request_url_second_level_domain TEXT
    );
    """

    JS = """
    CREATE TABLE IF NOT EXISTS javascript_leakage_data ( 
        original_id INTEGER PRIMARY KEY,
        visit_id INTEGER,
        site_url TEXT,
        value TEXT,
        func_name TEXT,
        script_url TEXT,
        document_url TEXT,
        top_level_url TEXT,
        arguments TEXT,
        encoding TEXT,
        top_level_url_second_level_domain TEXT,
        script_url_second_level_domain TEXT,
        document_url_second_level_domain TEXT
    );
    """

    COOKIES = """
    CREATE TABLE IF NOT EXISTS javascript_cookies_leakage_data ( 
        original_id INTEGER, 
        visit_id INTEGER,
        site_url TEXT,
        record_type TEXT,
        change_cause TEXT,
        expiry DATETIME,
        host TEXT,
        is_secure INTEGER,
        name TEXT,
        path TEXT,
        value TEXT,
        same_site TEXT,
        first_party_domain TEXT,
        encoding TEXT,
        site_url_second_level_domain TEXT,
        host_second_level_domain TEXT
    );
    """


class ThirdPartyTableCreationCommand(StrEnum):
    """Enum class to store SQL commands to create leakage tables"""

    HTTP_REQUESTS = """
    CREATE TABLE IF NOT EXISTS http_requests_third_party ( 
        original_id INTEGER PRIMARY KEY,
        visit_id INTEGER,
        site_url TEXT,
        request_id INTEGER,
        url TEXT,
        top_level_url TEXT,
        method TEXT NOT NULL,
        referrer TEXT,
        headers TEXT,
        post_body TEXT,
        post_body_raw TEXT,
        triggering_origin TEXT,
        loading_origin TEXT,
        loading_href TEXT,
        is_third_party_channel INTEGER,
        is_third_party_to_top_window INTEGER,
        is_XHR INTEGER,
        top_level_url_second_level_domain TEXT,
        request_url_second_level_domain TEXT
    );
    """

    JS = """
    CREATE TABLE IF NOT EXISTS javascript_third_party ( 
        original_id INTEGER PRIMARY KEY,
        visit_id INTEGER,
        site_url TEXT,
        value TEXT,
        func_name TEXT,
        script_url TEXT,
        document_url TEXT,
        top_level_url TEXT,
        arguments TEXT,
        top_level_url_second_level_domain TEXT,
        script_url_second_level_domain TEXT,
        document_url_second_level_domain TEXT
    );
    """

    COOKIES = """
    CREATE TABLE IF NOT EXISTS javascript_cookies_third_party ( 
        original_id INTEGER PRIMARY KEY,   
        visit_id INTEGER,
        site_url TEXT,
        record_type TEXT,
        change_cause TEXT,
        expiry DATETIME,
        host TEXT,
        is_secure INTEGER,
        name TEXT,
        path TEXT,
        value TEXT,
        same_site TEXT,
        first_party_domain TEXT,
        site_url_second_level_domain TEXT,
        host_second_level_domain TEXT
    );
    """


class LeakageDataQueries(Enum):
    """Enum class to store SQL queries about the leakage data obtained
    along with explanations of the queries
    """

    QUERIES = [
        {
            "explanation": "Sites crawled:",
            "queries": [
                {
                    "table_name": "site_visits",
                    "query": """
                SELECT COUNT(DISTINCT site_url) as sites_crawled
                FROM site_visits;
                """,
                }
            ],
        },
        {
            "explanation": "Incomplete visits:",
            "queries": [
                {
                    "table_name": "site_visits",
                    "query": """
                SELECT COUNT(DISTINCT visit_id) as incomplete_visits
                FROM incomplete_visits;
                """,
                }
            ],
        },
        {
            "explanation": "Total amount of HTTP Requests captured:",
            "queries": [
                {
                    "table_name": "http_requests",
                    "query": """
                SELECT COUNT(*) as http_requests_captured
                FROM http_requests;
                """,
                }
            ],
        },
        {
            "explanation": "Total amount of javascripts captured:",
            "queries": [
                {
                    "table_name": "javascript",
                    "query": """
                SELECT COUNT(*) as javascripts_captured
                FROM javascript;
                """,
                }
            ],
        },
        {
            "explanation": "Total amount of Cookies captured:",
            "queries": [
                {
                    "table_name": "javascript_cookies",
                    "query": """
                SELECT COUNT(*) as cookies_captured
                FROM javascript_cookies;
                """,
                }
            ],
        },
    ]

    def __getitem__(self, index):
        return self.value[index]


class ColumnsToSearch(Enum):
    """Enum class to store the relevant columns to search for leakages"""

    HTTP_REQUESTS = [
        "url",
        "referrer",
        "headers",
        "post_body",
        "post_body_raw",
    ]

    JS = [
        "value",
    ]

    COOKIES = [
        "name",
        "path",
        "value",
    ]

    def __getitem__(self, index):
        return self.value[index]


# Queries to get the data for the overall web resources captured by OpenWPM by site_url
class DetailsQueryBySiteURL:
    # TODO: 1. Add a column that is only the domain name of the search engine (e.g. google.com) so we can group by that and decouple from the search term
    #       2. Refactor this class
    def __init__(self, site_url) -> None:
        self.site_url = site_url
        self.HTTPRequests = self._get_http_data_query_by_url()
        self.JS = self._get_javascript_data_query_by_url()
        self.COOKIES = self._get_cookies_data_query_by_url()

    def _get_http_data_query_by_url(self):
        return (
            "SELECT  hr.url, "
            "        hr.top_level_url, "
            "        hr.referrer, "
            "        hr.headers, "
            "        hr.post_body, "
            "        hr.post_body_raw "
            "FROM http_requests hr "
            "INNER JOIN site_visits sv ON hr.visit_id = sv.visit_id "
            f"WHERE sv.site_url = '{self.site_url}'; "
        )

    def _get_javascript_data_query_by_url(self):
        return (
            "SELECT  js.value, "
            "        js.func_name, "
            "        js.script_url, "
            "        js.document_url, "
            "        js.top_level_url, "
            "        js.arguments "
            "FROM javascript js "
            "INNER JOIN site_visits sv ON js.visit_id = sv.visit_id "
            f"WHERE sv.site_url = '{self.site_url}';"
        )

    def _get_cookies_data_query_by_url(self):
        return (
            "SELECT  jsc.name, "
            "        jsc.path, "
            "        jsc.value, "
            "        jsc.same_site, "
            "        jsc.first_party_domain, "
            "        jsc.host, "
            "        jsc.is_secure "
            "FROM javascript_cookies jsc "
            "INNER JOIN site_visits sv ON jsc.visit_id = sv.visit_id "
            f"WHERE sv.site_url = '{self.site_url}';"
        )
