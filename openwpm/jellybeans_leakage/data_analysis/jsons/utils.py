def get_processed_cookie_row(row):
    # Unpack the row
    (
        name,
        path,
        value,
        same_site,
        first_party_domain,
        host,
        is_secure,
    ) = row
    cookie_list_element = {
        "host": host,
        "first_party_domain": first_party_domain,
        # Filled depending on where the leakage appears
        "name": name,
        "path": path,
        "value": value,
        "meatadata": {
            "same_site": same_site,
            "is_secure": is_secure,
        },
    }

    return cookie_list_element


def get_processed_javascript_row(row):
    # Unpack row columns from the table
    (
        value,
        func_name,
        script_url,
        document_url,
        top_level_url,
        arguments,
    ) = row

    # Set the leakage list element
    javascript_list_element = {
        "script_url": script_url,
        "top_level_url": top_level_url,
        "value": value,
        "metadata": {
            "document_url": document_url,
            "arguments": arguments,
            "func_name": func_name,
        },
    }

    return javascript_list_element


def get_processed_http_request_row(row):
    # Unpack row columns from the table
    (url, top_level_url, referrer, headers, post_body, post_body_raw) = row

    # Set the leakage list element
    http_request_list_element = {
        "url": url,
        "top_level_url": top_level_url,
        "metadata": {
            "referrer": referrer,
            "headers": headers,
            "post_body": post_body,
            "post_body_raw": post_body_raw,
        },
    }

    return http_request_list_element
