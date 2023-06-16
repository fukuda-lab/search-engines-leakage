import tldextract


class MatchingFunctions:
    """Class to store functions to match with the rulesets"""

    def __init__(self, ruleset_dict, len_http_requests, len_javascripts):
        self.RULESETS = ruleset_dict
        self.len_http_requests = len_http_requests
        self.len_javascripts = len_javascripts

    def _show_progress_requests(self, i):
        if i % 100 == 0:
            print(f"{round(i * 100 / self.len_http_requests, 2)}%")

    def _show_progress_javascripts(self, i):
        if i % 100 == 0:
            print(f"{round(i * 100 / self.len_javascripts, 2)}%")

    def _match_http_request_exceptionlist(self, request):
        # Bear in mind we might be over counting here
        # since we are not using the information of the request to comply with the exception rule's options
        # (e.g. we are not checking if the request is for a script, image, etc.)
        # This could be done by looking at Content-Type, but this might be too much.
        options = {
            "domain": tldextract.extract(request["top_level_url"]).registered_domain,
            "script": False,
            "image": False,
            "stylesheet": False,
            "object": False,
            "xmlhttprequest": False,
            "object-subrequest": False,
            "subdocument": False,
            "document": False,
            "elemhide": False,
            "other": False,
            "background": False,
            "xbl": False,
            "ping": False,
            "dtd": False,
            "media": False,
            "third-party": False,
            "match-case": False,
            "collapse": False,
            "donottrack": False,
            "websocket": False,
        }
        for rule in self.RULESETS["exception"].rules:
            if rule.match_url(request["url"], options):
                return True
        return False

    def _match_javascript_exceptionlist(self, javascript):
        options = {
            "domain": tldextract.extract(javascript["top_level_url"]).domain,
            "script": True,
            "image": False,
            "stylesheet": False,
            "object": False,
            "xmlhttprequest": False,
            "object-subrequest": False,
            "subdocument": False,
            "document": False,
            "elemhide": False,
            "other": False,
            "background": False,
            "xbl": False,
            "ping": False,
            "dtd": False,
            "media": False,
            "third-party": False,
            "match-case": False,
            "collapse": False,
            "donottrack": False,
            "websocket": False,
        }
        for rule in self.RULESETS["exception"].rules:
            if rule.match_url(javascript["script_url"], options):
                return True
        return False

    def get_http_request_matches(self, request):
        """
        Check if the request matches with any of the rules in the three rulesets.
        Returns a tuple with three booleans
        """
        url = request["url"]
        easylist = 1 if self.RULESETS["easylist"].should_block(url) else 0
        easyprivacy = 1 if self.RULESETS["easyprivacy"].should_block(url) else 0
        exception = 0
        if easylist or easyprivacy:
            # Only check for exceptions if the request matches with any of the rules in the rulesets
            exception = 1 if self._match_http_request_exceptionlist(request) else 0
        self._show_progress_requests(request["id"])
        return easylist, easyprivacy, exception

    def get_javascript_matches(self, javascript):
        """
        Check if the javascript matches with any of the rules in the three rulesets.
        Returns a tuple with three booleans
        """
        url = javascript["script_url"]
        easylist = 1 if self.RULESETS["easylist"].should_block(url) else 0
        easyprivacy = 1 if self.RULESETS["easyprivacy"].should_block(url) else 0
        exception = 0
        if easylist or easyprivacy:
            # Only check for exceptions if the request matches with any of the rules in the rulesets
            exception = 1 if self._match_javascript_exceptionlist(javascript) else 0
        self._show_progress_javascripts(javascript["id"])
        return easylist, easyprivacy, exception
