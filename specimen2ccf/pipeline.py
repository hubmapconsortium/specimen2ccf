import requests
from requests_file import FileAdapter
from specimen2ccf.ontology import SCOntology


def run(args):
    """
    """
    session = requests.Session()
    session.mount('file://', FileAdapter())

    o = SCOntology.new(args.ontology_iri)
    for url in args.input_url:
        response = session.get(url)
        data = response.json()
        o = o.mutate(data)

    o.serialize(args.output)
