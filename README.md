# Specimen2CCF
A Python tool to convert HuBMAP specimen data (i.e., donor, samples and datasets) to CCF Specimen Data Ontology.

## Installing the tool

You can install the application using `pip` after you clone the repository.
```
$ cd specimen2ccf
$ pip install .
```

## Using the tool

1. Download the raw specimen data from the [HuBMAP project repository](https://hubmap-link-api.herokuapp.com/hubmap-datasets?format=jsonld).

2. Run the tool
   ```
   $ specimen2ccf raw_data.jsonld --ontology-iri http://purl.org/ccf/data/specimen_dataset.owl -o specimen_dataset.owl
   ```

3. Open the resulting output file using [Protégé](https://protege.stanford.edu/)