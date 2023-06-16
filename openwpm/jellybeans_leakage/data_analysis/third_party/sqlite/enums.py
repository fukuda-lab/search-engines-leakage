from enum import StrEnum, Enum


class ABQueriesBySiteURL:
    # TODO: 1. Add a column that is only the domain name of the search engine (e.g. google.com) so we can group by that and decouple from the search term
    #       2. Refactor this class
    def __init__(self, site_url) -> None:
        self.site_url = site_url
        self.HTTPRequests = self._get_http_abp_matches()
        self.JS = self._get_javascript_abp_matches()

    def _get_http_abp_matches(self):
        return (
            "SELECT * "
            "FROM http_requests_third_party as third_party "
            "INNER JOIN adblock.http_requests_abp AS abp "
            "ON third_party.original_id = abp.id "
            f"WHERE third_party.site_url = '{self.site_url}' "
            f"AND abp.site_url = '{self.site_url}' ;"
        )

    def _get_javascript_abp_matches(self):
        return (
            "SELECT * "
            "FROM javascript_third_party as third_party "
            "INNER JOIN adblock.javascripts_abp AS abp "
            "ON third_party.original_id = abp.id "
            f"WHERE third_party.site_url = '{self.site_url}' "
            f"AND abp.site_url = '{self.site_url}' ;"
        )


class ABQueriesGeneral:
    QUERIES = [
        {
            "explanation": "Total number of matches for each ruleset in each table",
            "queries": [
                {
                    "table_name": "http_requests_abp",
                    "query": (
                        "SELECT COUNT(*) total, sum(easylist) as easylist,"
                        " sum(easyprivacy) as easyprivacy, sum(exceptionlist) as"
                        " exceptionlist "
                        "FROM http_requests_third_party as third_party "
                        "INNER JOIN adblock.http_requests_abp AS abp "
                        "ON third_party.original_id = abp.id "
                        "ORDER BY COUNT(*) DESC;"
                    ),
                },
                {
                    "table_name": "javascripts_abp",
                    "query": (
                        "SELECT COUNT(*) total, sum(easylist) as easylist,"
                        " sum(easyprivacy) as easyprivacy, sum(exceptionlist) as"
                        " exceptionlist "
                        "FROM javascript_third_party as third_party "
                        "INNER JOIN adblock.javascripts_abp AS abp "
                        "ON third_party.original_id = abp.id "
                        " ORDER BY COUNT(*) DESC;"
                    ),
                },
            ],
        },
        {
            "explanation": (
                "Number of matches for each ruleset for each site_url in each table"
            ),
            "queries": [
                {
                    "table_name": "http_requests_abp",
                    "query": (
                        "SELECT third_party.site_url as site_url, COUNT(*) total,"
                        " sum(easylist) as easylist, sum(easyprivacy) as easyprivacy,"
                        " sum(exceptionlist) as exceptionlist FROM"
                        " http_requests_third_party as third_party INNER JOIN"
                        " adblock.http_requests_abp AS abp ON third_party.original_id ="
                        " abp.id GROUP BY third_party.site_url ORDER BY COUNT(*) DESC;"
                    ),
                },
                {
                    "table_name": "javascripts_abp",
                    "query": (
                        "SELECT third_party.site_url as site_url, COUNT(*) total,"
                        " sum(easylist) as easylist, sum(easyprivacy) as easyprivacy,"
                        " sum(exceptionlist) as exceptionlist FROM"
                        " javascript_third_party as third_party INNER JOIN"
                        " adblock.javascripts_abp AS abp ON third_party.original_id ="
                        " abp.id GROUP BY third_party.site_url  ORDER BY COUNT(*) DESC;"
                    ),
                },
            ],
        },
    ]
