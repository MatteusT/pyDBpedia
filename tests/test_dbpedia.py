import pytest

from pydbpedia.pyDBpedia import (
    PyDBpedia,
    DEFAULT_ENDPOINT,
    parse_objects,
    format_url,
    RAW_QUERY,
    create_sparql_query,
    make_in_filter,
    parse_subject_object_tuples,
)
from pydbpedia import namespace


@pytest.fixture
def dbpedia_uris():
    return [
        "http://dbpedia.org/resource/Dublin",
        "http://dbpedia.org/resource/London",
        "http://dbpedia.org/resource/Albert_Einstein",
        "http://dbpedia.org/resource/Berlin",
        "http://dbpedia.org/resource/NBA",
    ]


@pytest.fixture
def expected_types():
    return [
        'http://dbpedia.org/ontology/Person',
        'http://dbpedia.org/ontology/Agent',
        'http://dbpedia.org/ontology/Scientist',
        'http://dbpedia.org/ontology/Place',
        'http://dbpedia.org/ontology/Location',
        'http://dbpedia.org/ontology/City',
        'http://dbpedia.org/ontology/PopulatedPlace',
        'http://dbpedia.org/ontology/Settlement',
        'http://dbpedia.org/ontology/Place',
        'http://dbpedia.org/ontology/Location',
        'http://dbpedia.org/ontology/City',
        'http://dbpedia.org/ontology/PopulatedPlace',
        'http://dbpedia.org/ontology/Settlement',
        'http://dbpedia.org/ontology/Place',
        'http://dbpedia.org/ontology/Location',
        'http://dbpedia.org/ontology/PopulatedPlace',
        'http://dbpedia.org/ontology/Settlement',
        'http://dbpedia.org/ontology/Agent',
        'http://dbpedia.org/ontology/BasketballLeague',
        'http://dbpedia.org/ontology/Organisation',
        'http://dbpedia.org/ontology/SportsLeague'
    ]


@pytest.fixture
def expected_locations():
    return [
        "http://dbpedia.org/resource/Dublin",
        "http://dbpedia.org/resource/London",
        "http://dbpedia.org/resource/Berlin",
    ]


def test_endpoint():
    dbpedia_wrapper = PyDBpedia(endpoint=DEFAULT_ENDPOINT)
    assert dbpedia_wrapper.endpoint == DEFAULT_ENDPOINT


def test_get_types(dbpedia_uris, expected_types):
    dbpedia_wrapper = PyDBpedia(endpoint=DEFAULT_ENDPOINT)
    objects = dbpedia_wrapper.get_objects(subjects=dbpedia_uris, predicates=[namespace.RDF_TYPE],
                                          redirect=True, contains="http://dbpedia.org/ontology/")
    # since dbpedia gets updated we want it to be alomst right in this case
    assert sum([etype in objects for etype in expected_types]) / len(expected_types) > 0.9
    assert all(["http://dbpedia.org/ontology/" in ptype for ptype in objects])


def test_get_locations(dbpedia_uris, expected_locations):
    in_list = ["http://dbpedia.org/ontology/Place", "http://dbpedia.org/ontology/Location"]
    dbpedia_wrapper = PyDBpedia(endpoint=DEFAULT_ENDPOINT)
    so_tuples = dbpedia_wrapper.get_subject_object_tuples(subjects=dbpedia_uris,
                                                          predicates=[namespace.RDF_TYPE],
                                                          in_list=in_list)
    location_entities = list(set([subj for subj, obj in so_tuples]))
    assert sorted(location_entities) == sorted(expected_locations)


def test_format_url():
    special_uri = "http://dbpedia.org/resource/Toys_\"R\"_Us"
    assert format_url(special_uri) == special_uri.replace("\"", "%22")


def test_create_sparql_query():
    subjects = ['http://dbpedia.org/resource/foo', 'http://dbpedia.org/resource/bar']
    predicates = ['http://dbpedia.org/resource/pred']
    contains = 'http://dbpedia.org/ontology/'
    in_list = ['http://dbpedia.org/ontology/Location', 'http://dbpedia.org/ontology/Place']
    expected_query_1 = RAW_QUERY.format(
        "<http://dbpedia.org/resource/foo> <http://dbpedia.org/resource/bar>",
        "<http://dbpedia.org/resource/pred>", "")

    expected_query_2 = RAW_QUERY.format(
        "<http://dbpedia.org/resource/foo> <http://dbpedia.org/resource/bar>",
        "<http://dbpedia.org/resource/pred>",
        """FILTER (strstarts(str(?object), "http://dbpedia.org/ontology/"))""")

    expected_query_3 = RAW_QUERY.format(
        "<http://dbpedia.org/resource/foo> <http://dbpedia.org/resource/bar>",
        "<http://dbpedia.org/resource/pred>",
        """FILTER (?object in (<http://dbpedia.org/ontology/Location>,"""
        """<http://dbpedia.org/ontology/Place>))""")

    query_1 = create_sparql_query(subjects=subjects, predicates=predicates, redirect=False)
    query_2 = create_sparql_query(subjects=subjects, predicates=predicates, contains=contains,
                                  redirect=False)
    query_3 = create_sparql_query(subjects=subjects, predicates=predicates, in_list=in_list,
                                  redirect=False)

    assert query_1 == expected_query_1
    assert query_2 == expected_query_2
    assert query_3 == expected_query_3

@pytest.mark.parametrize('expected,input', [
    ("""FILTER (?object in (<http://foo>,<http://bar>))""", ["http://foo", "http://bar"]),
    ("""FILTER (?object in (foo:obj,bar:obj))""", ["foo:obj", "bar:obj"]),
   ])
def test_make_in_filter(expected, input):
    result = make_in_filter(input)
    assert result == expected


def test_parse_objects(expected_types):
    dbpedia_output = {'results': {'bindings': [{'object': {'value': res}}
                                               for res in expected_types]}}
    result = parse_objects(dbpedia_output)
    assert sorted(result) == sorted(expected_types)


def test_parse_subject_object_tuples(expected_types):
    dbpedia_output = {'results': {'bindings': [{'object': {'value': res},
                                                'subject': {'value': res}}
                                               for res in expected_types]}}
    result = parse_subject_object_tuples(dbpedia_output)
    entities = []
    for object, subject in result:
        assert object == subject
        entities.append(object)
    assert sorted(entities) == sorted(expected_types)


def test_http_error_catch(dbpedia_uris, expected_types):
    dbpedia_wrapper = PyDBpedia(endpoint="http://httpstat.us/500")
    objects = dbpedia_wrapper.get_objects(subjects=dbpedia_uris, predicates=[namespace.RDF_TYPE],
                                          redirect=True, contains="http://dbpedia.org/ontology/")
    # since dbpedia gets updated we want it to be alomst right in this case
    assert sum([etype in objects for etype in expected_types])/len(expected_types) > 0.9
    assert all(["http://dbpedia.org/ontology/" in ptype for ptype in objects])


@pytest.mark.parametrize('uri,expected', [
    (['http://dbpedia.org/resource/Manchester_United'],
     ['http://dbpedia.org/resource/Manchester_United_F.C.']),
    (['http://dbpedia.org/resource/Manchester_United_F.C.'], []),
    (['http://dbpedia.org/resource/Beyonc%C3%A9'], [])
])
def test_disambiguation_redirect(uri, expected):
    dbpedia_wrapper = PyDBpedia()
    result = dbpedia_wrapper.get_objects(subjects=uri,
                                         predicates=[
                                             "http://dbpedia.org/ontology/wikiPageDisambiguates",
                                             "http://dbpedia.org/ontology/wikiPageRedirects"
                                         ], redirect=False)
    assert result == expected


@pytest.mark.parametrize('uri,expected', [
    (['http://dbpedia.org/resource/Manchester_United'],
     ['http://dbpedia.org/resource/Manchester_United_F.C.']),
    (['http://dbpedia.org/resource/Manchester_United_F.C.'], []),
    (['http://dbpedia.org/resource/Beyonc%C3%A9'], [])
])
def test_disambiguation_redirect(uri, expected):
    dbpedia_wrapper = PyDBpedia()
    result = dbpedia_wrapper.get_objects(subjects=uri,
                                         predicates=[
                                             "http://dbpedia.org/ontology/wikiPageDisambiguates",
                                             "http://dbpedia.org/ontology/wikiPageRedirects"
                                         ], redirect=False)
    assert result == expected