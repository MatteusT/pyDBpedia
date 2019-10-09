# pyDBpedia


### Installation

Can easily install using pip
```buildoutcfg
pip install pydbpedia
```

### Usage

A simple python package to query dbpedia without the need to use sparql query language. 

You will need add the endpoint as an argument when initiating the class `PyDBpedia`. 
```buildoutcfg
from pydbpedia import PyDBpedia, namespace

dbpedia_uris = ["http://dbpedia.org/resource/Manchester_United_F.C.", "http://dbpedia.org/resource/Albert_Einstein"]

dbpedia_wrapper = PyDBpedia(endpoint="http://dbpedia.org/sparql")
objects = dbpedia_wrapper.get_objects(subjects=dbpedia_uris, predicates=[namespace.RDF_TYPE])
```
Currently there are only two main functions which both take the same input parameters: 
* `subjects`: list of DBpedia URIs 
* `predicates`: list of predicates

Both Functions query DBpedia and return the results of the query given the `subjects` and `predicates`:
* `get_objects(subjects, predicates, **kwarg)`: Returns a list of simplified (without the DBpedia URI) DBpedia entities, for example `[Norway, Sweden]`.
* `get_subject_object_tuples(subjects, predicates, **kwarg)`:  Returns a list of format `[(subject, object),...]` where `subject` and `object` are simplified DBpedia entities, for example `[(Sweden, Stockholm), (Norway, Oslo)]`.

Additionally there is a possibilty to input filters to the two functions. The filters are set by sending them as additional input parameters. Currently there are three filters:
* `redirect`: Not really a filter but it will get the objects of the redirected resource. This is good to use when the resource is redirected and you still want to get the objects. For example: `get_objeccts(subjects=[http://dbpedia.org/resource/Man_U], predicate=[predicate], redirect=True)` will return the objects for the resource `http://dbpedia.org/resource/Manchester_United_F.C.` since it will be redirected to that.
* `contains`: Used to filter the objects of the query if they contain the inputed string. For example: `get_objects(subjects=[uri],predicates=[predicate],contains='http://dbpedia.org/Ontology/')'` will only return objects which are part of the dbpedia ontology (meaning that they contain `http://dbpedia.org/Ontology/`.
* `in_list`: To filter the objects of the query if they match any items in a list. For example:  `get_subject_object_tuples(subjects=[uri],predicates=[predicate],in_list=['London'])'` will only return all the cases where the objects are `London`.