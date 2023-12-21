LEAKAGES_CHART_QUERY_REQUEST = """
WITH http_requests AS (
    SELECT 
        visit_id,
        top_level_url_second_level_domain,
        request_url_second_level_domain AS receiver_url_second_level_domain,
        COUNT(*) as count_rows
    FROM http_requests_leakage_data
    GROUP BY visit_id, request_url_second_level_domain
),

javascript_requests AS (
    SELECT 
        visit_id,
        top_level_url_second_level_domain,
        script_url_second_level_domain AS receiver_url_second_level_domain,
        COUNT(*) as count_rows
    FROM javascript_leakage_data
    GROUP BY visit_id, script_url_second_level_domain
),

combined AS (
    SELECT 
        top_level_url_second_level_domain,
        receiver_url_second_level_domain,
        SUM(count_rows) as aggregated_count
    FROM (
        SELECT * FROM http_requests
        UNION ALL
        SELECT * FROM javascript_requests
    )
    GROUP BY visit_id, top_level_url_second_level_domain, receiver_url_second_level_domain
)

SELECT 
    top_level_url_second_level_domain,
    receiver_url_second_level_domain,
    SUM(aggregated_count) as total_count
FROM combined
GROUP BY top_level_url_second_level_domain, receiver_url_second_level_domain
ORDER BY top_level_url_second_level_domain, receiver_url_second_level_domain;
"""


lista_chart_leakages_tokyo = [
["ask (409)",	"google (339)", 339],
["ask (409)",	"google-analytics (60)", 60],
["ask (409)",	"statcounter (10)", 10],
["baidu (48)",	"bdstatic (48)", 48],
["bing (1)",	"bingparachute (1)", 1],
["naver (36)",	"pstatic (36)", 36],
["seznam (19)",	"gemius (9)",	9],
["seznam (19)",	"szn (10)", 10],
["sogou (11)",	"qq (11)",	11],
]



list_chart_leakages_santiago = [
["ask (403)",	"google (333)", 333],
["ask (403)",	"google-analytics (60)",	60],
["ask (403)",	"statcounter (10)", 10],
["baidu (106)", "bdstatic (106)",	106],
["bing (10)", "bingparachute (10)", 10],
["naver (20)", "pstatic (20)", 20],
["seznam (11)", "gemius (1)", 1],
["seznam (11)", "post (2)",	2],
["seznam (11)", "szn (8)", 8],
["sogou (22)", "qq (22)", 22],
]


list_chart_leakages_prague = [
["ask (414)",	"google (340)",	340],
["ask (414)",	"google-analytics (64)",	64],
["ask (414)",	"statcounter (10)",	10],
["baidu (119)",	"bdstatic (119)",	119],
["bing (1)",	"bingparachute (1)",	1],
["naver (20)",	"pstatic (20)",	20],
["seznam (11)",	"gemius (1)",	1],
["seznam (11)",	"szn (10)",	10],
["sogou (6)",	"qq (6)",	6],
]