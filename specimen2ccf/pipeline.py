import json
import requests

from urllib.parse import urlparse
from os.path import exists
from requests_file import FileAdapter

from specimen2ccf.ontology import SCOntology


def run(args):
    """
    """
    session = requests.Session()
    session.mount('file://', FileAdapter())

    o = SCOntology.new(args.ontology_iri)
    for url in args.input_file:
        data = json.load(open(url)) if is_local(url) \
            else session.get(url).json()
        o = o.mutate(data)

    o.serialize(args.output)


def is_local(url):
    url_parsed = urlparse(url)
    if url_parsed.scheme in ('file', ''):
        return exists(url_parsed.path)
    return False
