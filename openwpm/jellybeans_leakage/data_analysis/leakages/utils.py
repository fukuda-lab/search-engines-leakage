""" Some utility functions to have tidier code """


def get_processed_cookie_leakage(row):
    # Unpack the row
    (
        name,
        path,
        value,
        same_site,
        first_party_domain,
        host,
        is_secure,
        encoding,
    ) = row
    cookie_list_element = {
        "host": host,
        "first_party_domain": first_party_domain,
        # Filled depending on where the leakage appears
        "name": name,
        "path": path,
        "value": value,
        "meatadata": {
            "encoding": encoding,
            "same_site": same_site,
            "is_secure": is_secure,
        },
    }

    return cookie_list_element


def get_processed_javascript_leakage(row):
    # Unpack row columns from the table
    (
        value,
        func_name,
        script_url,
        document_url,
        top_level_url,
        arguments,
        encoding,
    ) = row

    # Set the leakage list element
    javascript_list_element = {
        "script_url": script_url,
        "top_level_url": top_level_url,
        "value": value,
        "metadata": {
            "arguments": arguments,
            "func_name": func_name,
            "document_url": document_url,
        },
        "encoding": encoding,
    }

    return javascript_list_element


def get_processed_http_leakage(row, search_terms):
    # First unpack the row from the table
    (
        url,
        top_level_url,
        referrer,
        headers,
        post_body,
        post_body_raw,
        encoding,
        is_third_party_channel,
        is_third_party_to_top_window,
        top_level_url_etld_plus_one,
        request_url_etld_plus_one,
    ) = row

    # Set the leakage list element
    http_list_element = {
        "request_url": url,
        "top_level_url": top_level_url,
        # Info that is relevant for every entry (we should be able to just delete it if we don't need it)
        # Info that will be different for every entry depending on the column of the leakage
        "explicit_leakage": {},
        "metadata": {
            # We could just pick more or delete what we don't need
            "is_third_party_channel": is_third_party_channel,
            "is_third_party_to_top_window": is_third_party_to_top_window,
            "encoding": encoding,
            "etlds": {
                "top_level_url_etld_plus_one": top_level_url_etld_plus_one,
                "request_url_etld_plus_one": request_url_etld_plus_one,
            },
        },
    }

    # Complete the explicit leakage info only where it appears
    # TODO: We are hard coding the SEARCH_TERM because we only found leakage with one encoding, so fix this if we find leakages with more encodings
    for term in search_terms:
        if term.lower() in (referrer or "").lower():
            http_list_element["explicit_leakage"]["referrer"] = referrer
        if term.lower() in (headers or "").lower():
            http_list_element["explicit_leakage"]["headers"] = headers
        if term.lower() in (post_body or "").lower():
            http_list_element["explicit_leakage"]["post_body"] = post_body
        if term.lower() in (post_body_raw or "").lower():
            http_list_element["explicit_leakage"]["post_body_raw"] = post_body_raw

    return http_list_element
