from specimen2ccf.namespace import CCF

from rdflib import Graph, URIRef, Literal
from rdflib import OWL, XSD, RDF, RDFS, DC, DCTERMS
from rdflib.extras.infixowl import Ontology, Property


class SCOntology:
    """CCF Specimen Data Ontology
    Represents the Specimen Data Ontology graph that can be mutated by
    supplying the HuBMAP specimen records
    """
    def __init__(self, graph=None):
        self.graph = graph

    @staticmethod
    def new(ontology_iri):
        g = Graph()
        g.bind('ccf', CCF)
        g.bind('owl', OWL)
        g.bind('dc', DC)
        g.bind('dcterms', DCTERMS)

        # Ontology properties
        Ontology(identifier=URIRef(ontology_iri), graph=g)

        # Declaration axioms
        Property(CCF.has_biological_sex, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.donates, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.donated_by, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.subdivided_into_sections, baseType=OWL.ObjectProperty,
                 graph=g)
        Property(CCF.generates_dataset, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.has_rui_location, baseType=OWL.ObjectProperty, graph=g)

        return SCOntology(g)

    def mutate(self, data):
        """
        """
        for obj in data['@graph']:
            object_type = obj['@type']
            if object_type == "Donor":
                self._add_donor(obj)

        return SCOntology(self.graph)

    def _add_donor(self, obj):
        donor_iri = self._uri(obj['@id'])
        self._add_donor_to_graph(
            donor_iri,
            self._string(obj['label']),  # more like a description
            self._string(obj['description']),  # more like a comment
            self._string(obj['link']),
            self._get_age(obj),
            self._get_biological_sex(obj),
            self._get_bmi(obj),
            self._string(obj['consortium_name']),
            self._string(obj['provider_name']),
            self._string(obj['provider_uuid']))
        self._add_samples(donor_iri, None, obj['samples'])

    def _add_donor_to_graph(self, donor_iri, description, comment, link,
                            age, biological_sex, bmi, consortium_name,
                            provider_name, provider_uuid):
        self.graph.add((donor_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((donor_iri, RDF.type, CCF.donor))
        self.graph.add((donor_iri, CCF.description, description))
        self.graph.add((donor_iri, RDFS.comment, comment))
        self.graph.add((donor_iri, CCF.url, link))
        if age is not None:
            self.graph.add((donor_iri, CCF.age, age))
        if biological_sex is not None:
            self.graph.add((donor_iri, CCF.has_biological_sex, biological_sex))
        if bmi is not None:
            self.graph.add((donor_iri, CCF.bmi, bmi))
        self.graph.add((donor_iri, CCF.consortium_name, consortium_name))
        self.graph.add((donor_iri, CCF.tissue_provider_name, provider_name))
        self.graph.add((donor_iri, CCF.tissue_provider_uuid, provider_uuid))

    def _add_samples(self, donor_iri, tissue_block, any_samples):
        for any_sample in any_samples:
            sample_type = any_sample['sample_type']
            if sample_type == "Tissue Block":
                tissue_block = any_sample
                tissue_block_iri = self._uri(tissue_block['@id'])
                rui_location_iri =\
                    self._uri(tissue_block['rui_location']['@id'])
                self._add_tissue_block_to_graph(
                    tissue_block_iri,
                    rui_location_iri,
                    donor_iri,
                    self._string(tissue_block['label']),  # more like a comment
                    self._string(tissue_block['description']),
                    self._string(tissue_block['link']),
                    self._integer(tissue_block['section_count']),
                    self._integer(tissue_block['section_size']),
                    self._string(tissue_block['section_units']))
                self._add_samples(donor_iri, tissue_block,
                                  tissue_block['sections'])
                self._add_datasets(tissue_block, tissue_block['datasets'])
            elif sample_type == "Tissue Section":
                tissue_section = any_sample
                if tissue_block is None:
                    raise ValueError("Tissue section has missing tissue block")
                tissue_block_iri = self._uri(tissue_block['@id'])
                tissue_section_iri = self._uri(tissue_section['@id'])
                self._add_tissue_section_to_graph(
                    tissue_block_iri,
                    tissue_section_iri,
                    donor_iri,
                    self._string(tissue_section['label']),  # more like a comment
                    self._string(tissue_section['description']),
                    self._string(tissue_section['link']),
                    self._integer(tissue_section['section_number']))
                self._add_samples(donor_iri, tissue_section,
                                  tissue_section['samples'])
                self._add_datasets(tissue_section, tissue_section['datasets'])

    def _add_tissue_block_to_graph(self, tissue_block_iri, rui_location_iri,
                                   donor_iri, comment, description, link,
                                   section_count, section_size,
                                   section_size_unit):
        self.graph.add((tissue_block_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((tissue_block_iri, RDF.type, CCF.tissue_block))
        self.graph.add((tissue_block_iri, CCF.has_rui_location,
                        rui_location_iri))
        self.graph.add((tissue_block_iri, CCF.donated_by, donor_iri))
        self.graph.add((donor_iri, CCF.donates, tissue_block_iri))
        self.graph.add((tissue_block_iri, RDFS.comment, comment))
        self.graph.add((tissue_block_iri, CCF.description, description))
        self.graph.add((tissue_block_iri, CCF.url, link))
        self.graph.add((tissue_block_iri, CCF.section_count, section_count))
        self.graph.add((tissue_block_iri, CCF.section_size, section_size))
        self.graph.add((tissue_block_iri, CCF.section_size_unit,
                        section_size_unit))

    def _add_tissue_section_to_graph(self, tissue_block_iri,
                                     tissue_section_iri, donor_iri,
                                     comment, description, link,
                                     section_number):
        self.graph.add((tissue_section_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((tissue_section_iri, RDF.type, CCF.tissue_section))
        self.graph.add((tissue_block_iri, CCF.subdivided_into_sections,
                        tissue_section_iri))
        self.graph.add((tissue_section_iri, CCF.donated_by, donor_iri))
        self.graph.add((donor_iri, CCF.donates, tissue_section_iri))
        self.graph.add((tissue_section_iri, RDFS.comment, comment))
        self.graph.add((tissue_section_iri, CCF.description, description))
        self.graph.add((tissue_section_iri, CCF.url, link))
        self.graph.add((tissue_section_iri, CCF.section_number,
                        section_number))

    def _add_datasets(self, any_sample, datasets):
        for dataset in datasets:
            self._add_dataset_to_graph(
                self._uri(dataset['@id']),
                self._uri(any_sample['@id']),
                self._string(dataset['label']),  # more like a comment
                self._string(dataset['description']),
                self._string(dataset['link']),
                self._string(dataset['technology']),
                self._string(dataset['thumbnail']))

    def _add_dataset_to_graph(self, dataset_iri, sample_iri, comment,
                              description, link, technology, thumbnail):
        self.graph.add((dataset_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((dataset_iri, RDF.type, CCF.dataset))
        self.graph.add((sample_iri, CCF.generates_dataset, dataset_iri))
        self.graph.add((dataset_iri, RDFS.comment, comment))
        self.graph.add((dataset_iri, CCF.description, description))
        self.graph.add((dataset_iri, CCF.url, link))
        self.graph.add((dataset_iri, CCF.technology, technology))
        self.graph.add((dataset_iri, CCF.thumbnail, thumbnail))

    def _get_age(self, obj):
        try:
            return self._integer(obj['age'])
        except KeyError:
            return None

    def _get_bmi(self, obj):
        try:
            return self._decimal(obj['bmi'])
        except KeyError:
            return None

    def _get_biological_sex(self, obj):
        try:
            biological_sex = None
            if obj['sex'] == "Male":
                biological_sex =\
                    self._uri("http://purl.bioontology.org/ontology/LNC/LA2-8")
            elif obj['sex'] == "Female":
                biological_sex =\
                    self._uri("http://purl.bioontology.org/ontology/LNC/LA3-6")
            return biological_sex
        except KeyError:
            return None

    def _uri(self, str):
        return URIRef(str)

    def _string(self, str):
        return Literal(str)

    def _integer(self, str):
        return Literal(str, datatype=XSD.integer)

    def _decimal(self, str):
        return Literal(str, datatype=XSD.decimal)

    def _date(self, str):
        return Literal(str, datatype=XSD.date)

    def serialize(self, destination):
        """
        """
        self.graph.serialize(format='ttl', destination=destination)
