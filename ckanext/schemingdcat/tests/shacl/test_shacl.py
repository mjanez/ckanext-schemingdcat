import json
import os
import logging

from rdflib import URIRef
from pyshacl import validate
import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFSerializer
from ckanext.schemingdcat.tests.utils import get_file_contents


log = logging.getLogger(__name__)

generated_graphs = {}

dataset_files = {
    "dcat_ap_2_full_dataset": "ckan_full_dataset_dcat_ap_2.json",
    "dcat_ap_2_legacy_dataset": "ckan_full_dataset_dcat_ap_2_legacy.json",
    "dcat_ap_2_vocabularies_dataset": "ckan_full_dataset_dcat_ap_2_vocabularies.json"
}

def _get_shacl_file_path(shacl_type, version=None):
    """
    Return the path to a SHACL ttl file shipped with the tests, or None if missing.

    Files live in ``tests/shacl/<version>/``, not ``tests/shacl/shacl/<version>/``.

    Args:
        shacl_type (str): Either a suffix type (e.g. 'shapes', 'shapes_recommended',
            'range') or a full filename ending in ``.ttl``.
        version (str, optional): DCAT-AP version directory (e.g. '2.1.1', '3.0.0').
            Required when ``shacl_type`` is not a full filename.

    Returns:
        str or None: Absolute path if the file exists, otherwise None.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if shacl_type.endswith(".ttl"):
        file_name = os.path.basename(shacl_type)
    else:
        if not version:
            return None
        shacl_type = shacl_type.strip("_").replace("shacl_", "", 1)
        file_name = "dcat-ap_{version}_shacl_{shacl_type}.ttl".format(
            version=version, shacl_type=shacl_type
        )

    candidates = []
    if version:
        candidates.append(os.path.join(base_dir, version, file_name))
    try:
        for entry in os.listdir(base_dir):
            cand = os.path.join(base_dir, entry, file_name)
            if cand not in candidates:
                candidates.append(cand)
    except OSError:
        pass

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _require_shacl_file(shacl_type, version=None):
    """Return a SHACL file path or skip the test if it is not in the repo."""
    path = _get_shacl_file_path(shacl_type, version)
    if not path:
        pytest.skip(
            "SHACL file not available in the repo (optional): {0} {1}".format(
                shacl_type, version or ""
            )
        )
    return path

def graph_from_dataset(dataset_key):
    """
    Generates an RDF graph from a dataset identified by the given key.

    This function retrieves the dataset file name from the `dataset_files` dictionary
    using the provided `dataset_key`. If the dataset has not been previously processed,
    it reads the dataset file, creates the dataset, serializes it into an RDF graph,
    and stores the graph in the `generated_graphs` dictionary.

    Args:
        dataset_key (str): The key identifying the dataset in the `dataset_files` dictionary.

    Returns:
        rdflib.Graph: The RDF graph generated from the dataset.
    """
    global generated_graphs

    file_name = dataset_files.get(dataset_key)
    if not file_name:
        pytest.skip(
            "No JSON dataset fixture registered for key {0!r}".format(dataset_key)
        )

    if not generated_graphs.get(file_name):
        if not file_name.startswith("ckan/"):
            file_name = "ckan/" + file_name
        try:
            dataset_dict = json.loads(get_file_contents(file_name))
        except (OSError, IOError):
            pytest.skip("Dataset fixture file missing: {0}".format(file_name))
       
        # Log the dataset_dict
        #log.info(f"Generated dataset_dict: {json.dumps(dataset_dict, indent=2)}")
        
        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        s.graph_from_dataset(dataset)

        generated_graphs[file_name] = s.g

    return generated_graphs[file_name]


def _results_count(results_graph):
    return len(
        [
            t
            for t in results_graph.triples(
                (None, URIRef("http://www.w3.org/ns/shacl#result"), None)
            )
        ]
    )


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.schemingdcat:schemas/geodcat_ap/es_geodcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.schemingdcat:schemas/default_presets.json ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "eu_dcat_ap_2 eu_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes():

    graph = graph_from_dataset("dcat_ap_2_full_dataset")

    # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
    # literal range, and cardinalities.
    path = _require_shacl_file("shapes", "2.1.1")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.schemingdcat:schemas/geodcat_ap/es_geodcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.schemingdcat:schemas/default_presets.json ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "eu_dcat_ap_2 eu_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes_recommended():

    graph = graph_from_dataset("dcat_ap_2_full_dataset")

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _require_shacl_file("shapes_recommended", "2.1.1")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


# @pytest.mark.usefixtures("with_plugins", "clean_db")
# @pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
# @pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "eu_dcat_ap_2")
# def test_validate_dcat_ap_2_legacy_graph_shapes():

#     graph = graph_from_dataset("dcat_ap_2_legacy_dataset")

#     # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
#     # literal range, and cardinalities.
#     path = _get_shacl_file_path("shapes", "2.1.1")
#     r = validate(graph, shacl_graph=path)
#     conforms, results_graph, results_text = r
#     assert conforms, results_text


# @pytest.mark.usefixtures("with_plugins", "clean_db")
# @pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
# @pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "eu_dcat_ap_2")
# def test_validate_dcat_ap_2_legacy_graph_shapes_recommended():

#     graph = graph_from_dataset("dcat_ap_2_legacy_dataset")

#     # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
#     # of recommended properties.
#     path = _get_shacl_file_path("shapes_recommended", "2.1.1")
#     r = validate(graph, shacl_graph=path)
#     conforms, results_graph, results_text = r
#     assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.schemingdcat:schemas/geodcat_ap/es_geodcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.schemingdcat:schemas/default_presets.json ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "eu_dcat_ap_2 eu_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes_range():

    graph = graph_from_dataset("dcat_ap_2_vocabularies_dataset")

    # dcat-ap_2.1.1_shacl_range.ttl: constraints concerning object range
    path = _require_shacl_file("range", "2.1.1")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
        "Value does not have class adms:Identifier",
        "Value does not have class dct:Frequency",
        "Value does not have class dct:LicenseDocument",
        "Value does not have class dct:MediaType",
        "Value does not have class dct:MediaTypeOrExtent",
        "Value does not have class dct:RightsStatement",
        "Value does not have class dct:Standard",
        # Qualified relations
        "Value does not conform to Shape :DcatResource_Shape. See details for more information.",
        "The node is either a Catalog, Dataset or a DataService",
    ]

    assert set(failures) - set(known_failures) == set(), results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_3")
def test_validate_dcat_ap_3_graph():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_vocabularies.json")

    path = _require_shacl_file("shapes", "3.0.0")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
    ]

    assert set(failures) - set(known_failures) == set(), results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_us_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "dcat_us_3")
def test_validate_dcat_us_3_graph():

    graph = graph_from_dataset("ckan_full_dataset_dcat_us_vocabularies.json")

    path = _require_shacl_file("dcat-us_3.0_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
    ]

    assert set(failures) - set(known_failures) == set(), results_text
