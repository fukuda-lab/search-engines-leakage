from enum import StrEnum, Enum


class CrawledDataQueryForABP(StrEnum):
    """Enum class to store SQL queries to retrieve crawled data"""

    HTTP_REQUESTS = """
    SELECT hr.id, 
        sv.visit_id, 
        sv.site_url, 
        hr.url, 
        hr.top_level_url
    FROM site_visits sv 
    INNER JOIN http_requests hr ON sv.visit_id = hr.visit_id;
    """

    JS = """
    SELECT js.id, 
        sv.visit_id, 
        sv.site_url, 
        js.script_url, 
        js.document_url, 
        js.top_level_url
    FROM site_visits sv 
    INNER JOIN javascript js ON sv.visit_id = js.visit_id; 
    """


class CreateABPTablesCommands(StrEnum):
    """Enum class to store SQL queries to create tables for ABP"""

    HTTP_REQUESTS = """
    CREATE TABLE IF NOT EXISTS http_requests_abp ( 
        id INTEGER PRIMARY KEY, 
        visit_id INTEGER, 
        site_url TEXT, 
        url TEXT, 
        top_level_url TEXT, 
        easylist INTEGER, 
        easyprivacy INTEGER, 
        exceptionlist INTEGER 
    ); 
    """

    JS = """
    CREATE TABLE IF NOT EXISTS javascripts_abp ( 
        id INTEGER PRIMARY KEY, 
        visit_id INTEGER, 
        site_url TEXT, 
        script_url TEXT, 
        document_url TEXT, 
        top_level_url TEXT, 
        easylist INTEGER, 
        easyprivacy INTEGER, 
        exceptionlist INTEGER 
    );
    """


class ABPQueries:
    """Enum class to store SQL queries to retrieve ABP data"""

    ALL_HTTP_REQUESTS = """
    SELECT * FROM http_requests_abp 
    WHERE easylist = 1 OR easyprivacy = 1 OR exceptionlist = 1 
    AND site_url = ? ;
    """

    ALL_JS = """
    SELECT * FROM javascripts_abp 
    WHERE easylist = 1 OR easyprivacy = 1 OR exceptionlist = 1 
    AND site_url = ? ;
    """
