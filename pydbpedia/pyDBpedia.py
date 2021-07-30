import logging
from urllib.parse import quote, urljoin
from urllib.error import HTTPError
import socket
from collections import OrderedDict

import requests

logger = logging.getLogger(__name__)


RAW_QUERY = """
SELECT ?subject ?object
WHERE {{
    VALUES ?subject {{ {0} }}
    VALUES ?predicate {{ {1} }}
    {{ ?subject ?predicate ?object }}
    {2}
}}"""

REDIRECT = """
UNION {
    ?subject <http://dbpedia.org/ontology/wikiPageRedirects> ?redirect .
    ?redirect ?predicate ?object
}"""
CONTAINS_FILTER = """FILTER (strstarts(str(?object), "{}"))"""
IN_FILTER = """FILTER (?object in ({}))"""


DBR = "http://dbpedia.org/resource/"
DEFAULT_ENDPOINT = "http://dbpedia.org/sparql"


def format_item(thing):
    if "http" in thing:
        return "<{}>".format(thing)
    return thing


def make_in_filter(uris):
    formatted_uris = [format_item(uri) for uri in uris]
    return IN_FILTER.format(",".join(formatted_uris))


def make_contains_filter(contains):
    return CONTAINS_FILTER.format(contains)


def make_redirect(do_redirect):
    if do_redirect:
        return REDIRECT
    else:
        return ""


def parse_objects(result):
    return [res['object']['value'] for res in result['results']['bindings']]


def parse_subject_object_tuples(result):
    return [(res['subject']['value'], res['object']['value'])
            for res in result['results']['bindings']]


def format_url(dbpedia_uri):
    return urljoin(DBR, quote(dbpedia_uri.replace(DBR, "")))


FILTER_TYPES = OrderedDict(
    redirect=make_redirect,
    in_list=make_in_filter,
    contains=make_contains_filter,
)


def make_filters(filters):
    filter_string = ""
    for filter, filter_function in FILTER_TYPES.items():
        if filter in filters:
            filter_string += filter_function(filters[filter])
    return filter_string


def create_sparql_query(subjects, predicates, **filters):
    subjects = [format_item(format_url(subject)) for subject in subjects]
    predicates = [format_item(predicate) for predicate in predicates]
    if "redirect" not in filters:
        filters["redirect"] = True
    filters = make_filters(filters)
    sparql_query = RAW_QUERY.format(" ".join(subjects), " ".join(predicates), filters)
    return sparql_query


class PyDBpedia:

    def __init__(self, endpoint=DEFAULT_ENDPOINT, timeout_sec=120):
        self.endpoint = endpoint
        self.timeout_sec = timeout_sec

    def _query_dbpedia(self, query, url=None):
        if not url:
            url = self.endpoint
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=self.timeout_sec)
        r.raise_for_status()
        return r.json()

    def _process_query(self, subjects, predicates, **kwargs):
        sparql_query = create_sparql_query(subjects, predicates, **kwargs)
        try:
            result = self._query_dbpedia(query=sparql_query)
        except (TimeoutError, HTTPError, requests.exceptions.HTTPError,
                requests.exceptions.Timeout, socket.timeout) as error:
            logger.exception("Call to pydbpedia endpoint %s failed with an expected error"
                             "sending subjects %s  and predicates %s  "
                             "resulting to the following query: %s",
                             self.endpoint, subjects, predicates, sparql_query)
            if self.endpoint != DEFAULT_ENDPOINT:
                result = self._query_dbpedia(query=sparql_query, url=DEFAULT_ENDPOINT)
            else:
                raise HTTPError("Cannot connect to DBpedia Endpoint: %s", error)
        return result

    def get_objects(self, subjects, predicates, **kwargs):
        return parse_objects(self._process_query(subjects, predicates, **kwargs))

    def get_subject_object_tuples(self, subjects, predicates, **kwargs):
        return parse_subject_object_tuples(self._process_query(subjects, predicates, **kwargs))
