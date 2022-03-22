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
        Property(CCF.provides, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.comes_from, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.part_of_tissue_block, baseType=OWL.ObjectProperty,
                 graph=g)
        Property(CCF.subdivided_into_sections, baseType=OWL.ObjectProperty,
                 graph=g)
        Property(CCF.generates_dataset, baseType=OWL.ObjectProperty, graph=g)
        Property(CCF.has_registration_location, baseType=OWL.ObjectProperty,
                 graph=g)

        return SCOntology(g)

    def mutate(self, data):
        """
        """
        data_array = data
        if isinstance(data, dict):
            data_array = data['@graph']
        for obj in data_array:
            publisher = self._get_publisher(obj)
            self._add_specimen_data(obj, publisher)
        return SCOntology(self.graph)

    def _add_specimen_data(self, obj, publisher):
        object_type = obj['@type']
        if object_type == "Donor":
            self._add_donor(obj, publisher)
        else:
            raise ValueError("Unknown object_type <" + object_type + ">")

    def _add_donor(self, obj, publisher):
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
            self._get_provider_name(obj),
            self._get_provider_uuid(obj),
            publisher)
        if 'samples' in obj:
            self._add_samples(donor_iri, None, obj['samples'], publisher)

    def _add_donor_to_graph(self, donor_iri, description, comment, link,
                            age, biological_sex, bmi, consortium_name,
                            provider_name, provider_uuid, publisher):
        self.graph.add((donor_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((donor_iri, RDF.type, CCF.donor))
        self.graph.add((donor_iri, CCF.description, description))
        self.graph.add((donor_iri, RDFS.comment, comment))
        self.graph.add((donor_iri, CCF.url, link))
        if age:
            self.graph.add((donor_iri, CCF.age, age))
        if biological_sex:
            self.graph.add((donor_iri, CCF.has_biological_sex, biological_sex))
        if bmi:
            self.graph.add((donor_iri, CCF.bmi, bmi))
        self.graph.add((donor_iri, CCF.consortium_name, consortium_name))
        if provider_name:
            self.graph.add((donor_iri, CCF.tissue_provider_name, provider_name))
        if provider_uuid:
            self.graph.add((donor_iri, CCF.tissue_provider_uuid, provider_uuid))
        self.graph.add((donor_iri, DCTERMS.publisher, publisher))

    def _add_samples(self, donor_iri, tissue_block, any_samples, publisher):
        for any_sample in any_samples:
            sample_type = any_sample['sample_type']
            if sample_type == "Tissue Block":
                tissue_block = any_sample
                tissue_block_iri = self._uri(tissue_block['@id'])
                registration_location_iri =\
                    self._uri(tissue_block['rui_location']['@id'])
                self._add_tissue_block_to_graph(
                    tissue_block_iri,
                    registration_location_iri,
                    donor_iri,
                    self._string(sample_type),
                    self._string(tissue_block['label']),  # more like a comment
                    self._string(tissue_block['description']),
                    self._string(tissue_block['link']),
                    self._integer(tissue_block['section_count']),
                    self._integer(tissue_block['section_size']),
                    self._string(tissue_block['section_units']),
                    publisher)
                if 'sections' in tissue_block:
                    self._add_samples(donor_iri,
                                      tissue_block,
                                      tissue_block['sections'],
                                      publisher)
                if 'datasets' in tissue_block:
                    self._add_datasets(tissue_block,
                                       tissue_block['datasets'],
                                       publisher)
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
                    self._string(sample_type),
                    self._string(tissue_section['label']),  # more like a comment
                    self._string(tissue_section['description']),
                    self._string(tissue_section['link']),
                    self._integer(tissue_section['section_number']),
                    publisher)
                if 'samples' in tissue_section:
                    self._add_samples(donor_iri,
                                      tissue_section,
                                      tissue_section['samples'],
                                      publisher)
                if 'datasets' in tissue_section:
                    self._add_datasets(tissue_section,
                                       tissue_section['datasets'],
                                       publisher)

    def _add_tissue_block_to_graph(self, tissue_block_iri,
                                   registration_location_iri,
                                   donor_iri, sample_type, comment,
                                   description, link,
                                   section_count, section_size,
                                   section_size_unit, publisher):
        self.graph.add((tissue_block_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((tissue_block_iri, RDF.type, CCF.tissue_block))
        self.graph.add((tissue_block_iri, CCF.has_registration_location,
                        registration_location_iri))
        self.graph.add((tissue_block_iri, CCF.comes_from, donor_iri))
        self.graph.add((donor_iri, CCF.provides, tissue_block_iri))
        self.graph.add((tissue_block_iri, CCF.sample_type, sample_type))
        self.graph.add((tissue_block_iri, RDFS.comment, comment))
        self.graph.add((tissue_block_iri, CCF.description, description))
        self.graph.add((tissue_block_iri, CCF.url, link))
        self.graph.add((tissue_block_iri, CCF.section_count, section_count))
        self.graph.add((tissue_block_iri, CCF.section_size, section_size))
        self.graph.add((tissue_block_iri, CCF.section_size_unit,
                        section_size_unit))
        self.graph.add((tissue_block_iri, DCTERMS.publisher, publisher))

    def _add_tissue_section_to_graph(self, tissue_block_iri,
                                     tissue_section_iri, donor_iri,
                                     sample_type, comment, description,
                                     link, section_number, publisher):
        self.graph.add((tissue_section_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((tissue_section_iri, RDF.type, CCF.tissue_section))
        self.graph.add((tissue_section_iri, CCF.part_of_tissue_block,
                        tissue_block_iri))
        self.graph.add((tissue_block_iri, CCF.subdivided_into_sections,
                        tissue_section_iri))
        self.graph.add((tissue_section_iri, CCF.comes_from, donor_iri))
        self.graph.add((donor_iri, CCF.provides, tissue_section_iri))
        self.graph.add((tissue_section_iri, CCF.sample_type, sample_type))
        self.graph.add((tissue_section_iri, RDFS.comment, comment))
        self.graph.add((tissue_section_iri, CCF.description, description))
        self.graph.add((tissue_section_iri, CCF.url, link))
        self.graph.add((tissue_section_iri, CCF.section_number,
                        section_number))
        self.graph.add((tissue_section_iri, DCTERMS.publisher, publisher))

    def _add_datasets(self, any_sample, datasets, publisher):
        for dataset in datasets:
            self._add_dataset_to_graph(
                self._uri(dataset['@id']),
                self._uri(any_sample['@id']),
                self._string(dataset['label']),  # more like a comment
                self._string(dataset['description']),
                self._string(dataset['link']),
                self._string(dataset['technology']),
                self._string(dataset['thumbnail']),
                publisher)

    def _add_dataset_to_graph(self, dataset_iri, sample_iri, comment,
                              description, link, technology, thumbnail,
                              publisher):
        self.graph.add((dataset_iri, RDF.type, OWL.NamedIndividual))
        self.graph.add((dataset_iri, RDF.type, CCF.dataset))
        self.graph.add((sample_iri, CCF.generates_dataset, dataset_iri))
        self.graph.add((dataset_iri, RDFS.comment, comment))
        self.graph.add((dataset_iri, CCF.description, description))
        self.graph.add((dataset_iri, CCF.url, link))
        self.graph.add((dataset_iri, CCF.technology, technology))
        self.graph.add((dataset_iri, CCF.thumbnail, thumbnail))
        self.graph.add((dataset_iri, DCTERMS.publisher, publisher))

    def _get_publisher(self, obj):
        try:
            return self._string(obj['consortium_name'])
        except KeyError:
            return None

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

    def _get_provider_name(self, obj):
        try:
            return self._string(obj['provider_name'])
        except KeyError:
            return None

    def _get_provider_uuid(self, obj):
        try:
            return self._string(obj['provider_uuid'])
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
