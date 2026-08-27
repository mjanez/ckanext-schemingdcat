import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.tests.utils import BaseParseTest

_ACCESS_RIGHTS_PUBLIC = (
    "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
)
_DCAT_TYPE_DATASET = (
    "http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset"
)
_LANG_ENG = "http://publications.europa.eu/resource/authority/language/ENG"
_LANG_SPA = "http://publications.europa.eu/resource/authority/language/SPA"
_EU_LANG = {
    "en": _LANG_ENG,
    "eng": _LANG_ENG,
    "es": _LANG_SPA,
    "spa": _LANG_SPA,
}


def _map_languages(values):
    if isinstance(values, str):
        values = [values]
    mapped = []
    for value in values or []:
        if isinstance(value, str) and value.startswith("http"):
            uri = value
        else:
            uri = _EU_LANG.get((value or "").lower())
        if uri and uri not in mapped:
            mapped.append(uri)
    return mapped


def _first_eu_language(values):
    mapped = _map_languages(values)
    if _LANG_ENG in mapped:
        return _LANG_ENG
    return mapped[0] if mapped else _LANG_ENG


def _adapt_parsed_dataset_for_eu_schema(dataset_dict):
    """Map generic DCAT fixture values to eu_dcat_ap_full.yaml choice URIs."""
    if dataset_dict.get("access_rights") == "public":
        dataset_dict["access_rights"] = _ACCESS_RIGHTS_PUBLIC
    if dataset_dict.get("dcat_type") == "test-type":
        dataset_dict["dcat_type"] = _DCAT_TYPE_DATASET
    if dataset_dict.get("language"):
        dataset_dict["language"] = _first_eu_language(dataset_dict["language"])
    for resource in dataset_dict.get("resources") or []:
        if resource.get("language"):
            resource["language"] = _first_eu_language(resource["language"])
        for service in resource.get("access_services") or []:
            desc = service.get("endpoint_description")
            if desc and not str(desc).startswith(("http://", "https://")):
                service["endpoint_description"] = (
                    "http://example.org/endpoint-description"
                )
    return dataset_dict


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat harvest schemingdcat_datasets schemingdcat fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.schemingdcat:schemas/dcat_ap/eu_dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.schemingdcat:schemas/default_presets.json ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "eu_dcat_ap_3 eu_dcat_ap_scheming"
)
class TestSchemingDCATParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with
        package_create and check that all expected fields are there
        """
        contents = self._get_file_contents("dcat/dataset.rdf")

        p = RDFParser()

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset_dict = datasets[0]

        assert dataset_dict["access_rights"] == "public"
        assert dataset_dict["dcat_type"] == "test-type"
        assert sorted(dataset_dict["language"]) == ["ca", "en", "es"]

        dataset_dict["name"] = "test-dcat-1"
        _adapt_parsed_dataset_for_eu_schema(dataset_dict)
        dataset = call_action("package_create", **dataset_dict)

        # Core fields

        assert dataset["title"] == "Zimbabwe Regional Geochemical Survey."
        assert (
            dataset["notes"]
            == "During the period 1982-86 a team of geologists from the British Geological Survey ..."
        )
        assert dataset["url"] == "http://dataset.info.org"
        assert dataset["version"] == "2.3"
        assert dataset["license_id"] == "cc-nc"
        assert sorted([t["name"] for t in dataset["tags"]]) == [
            "exploration",
            "geochemistry",
            "geology",
        ]

        # Standard fields
        assert dataset["version_notes"] == "New schema added"
        assert dataset["identifier"] == u"9df8df51-63db-37a8-e044-0003ba9b0d98"
        assert dataset["frequency"] == "http://purl.org/cld/freq/daily"
        assert dataset["access_rights"] == _ACCESS_RIGHTS_PUBLIC
        assert dataset["provenance"] == "Some statement about provenance"
        assert dataset["dcat_type"] == _DCAT_TYPE_DATASET

        assert dataset["issued"] == u"2012-05-10"
        assert dataset["modified"] == u"2012-05-10T21:04:00"
        assert dataset["temporal_resolution"] == "PT15M"
        assert dataset["spatial_resolution_in_meters"] == "1.5"

        # List fields
        assert sorted(dataset["conforms_to"]) == ["Standard 1", "Standard 2"]
        assert dataset["language"] == _LANG_ENG
        assert sorted(dataset["theme"]) == [
            "Earth Sciences",
            "http://eurovoc.europa.eu/100142",
            "http://eurovoc.europa.eu/209065",
        ]
        assert sorted(dataset["alternate_identifier"]) == [
            "alternate-identifier-1",
            "alternate-identifier-2",
        ]
        assert sorted(dataset["documentation"]) == [
            "http://dataset.info.org/doc1",
            "http://dataset.info.org/doc2",
        ]

        assert sorted(dataset["is_referenced_by"]) == [
            "https://doi.org/10.1038/sdata.2018.22",
            "test_isreferencedby",
        ]
        assert sorted(dataset["applicable_legislation"]) == [
            "http://data.europa.eu/eli/reg_impl/2023/138/oj",
            "http://data.europa.eu/eli/reg_impl/2023/138/oj_alt",
        ]
        # Repeating subfields

        assert dataset["contact"][0]["name"] == "Point of Contact"
        assert dataset["contact"][0]["email"] == "contact@some.org"

        assert (
            dataset["publisher"][0]["name"] == "Publishing Organization for dataset 1"
        )
        assert dataset["publisher"][0]["email"] == "contact@some.org"
        assert dataset["publisher"][0]["url"] == "http://some.org"
        assert (
            dataset["publisher"][0]["type"]
            == "http://purl.org/adms/publishertype/NonProfitOrganisation"
        )
        assert dataset["temporal_coverage"][0]["start"] == "1905-03-01"
        assert dataset["temporal_coverage"][0]["end"] == "2013-01-05"

        resource = dataset["resources"][0]

        # Resources: core fields
        assert resource["url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"

        # Resources: standard fields
        assert resource["license"] == "http://creativecommons.org/licenses/by-nc/2.0/"
        assert resource["rights"] == "Some statement about rights"
        assert resource["issued"] == "2012-05-11"
        assert resource["modified"] == "2012-05-01T00:04:06"
        assert resource["status"] == "http://purl.org/adms/status/Completed"
        assert resource["size"] == 12323
        assert (
            resource["availability"]
            == "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL"
        )
        assert (
            resource["compress_format"]
            == "http://www.iana.org/assignments/media-types/application/gzip"
        )
        assert (
            resource["package_format"]
            == "http://publications.europa.eu/resource/authority/file-type/TAR"
        )

        assert resource["hash"] == "4304cf2e751e6053c90b1804c89c0ebb758f395a"
        assert (
            resource["hash_algorithm"]
            == "http://spdx.org/rdf/terms#checksumAlgorithm_sha1"
        )

        assert (
            resource["access_url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"
        )
        assert "download_url" not in resource

        # Resources: list fields
        assert resource["language"] == _LANG_ENG
        assert sorted(resource["documentation"]) == [
            "http://dataset.info.org/distribution1/doc1",
            "http://dataset.info.org/distribution1/doc2",
        ]
        assert sorted(resource["conforms_to"]) == ["Standard 1", "Standard 2"]

        # Resources: repeating subfields
        assert resource["access_services"][0]["title"] == "Sparql-end Point"
        assert resource["access_services"][0]["endpoint_url"] == [
            "http://publications.europa.eu/webapi/rdf/sparql"
        ]
        assert resource["access_services"][0]["endpoint_description"] == (
            "http://example.org/endpoint-description"
        )
