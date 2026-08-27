import pytest

from rdflib.term import URIRef

from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import BaseSerializeTest

from ckanext.dcat.profiles import (
    RDF,
    DCAT,
    DCT,
    ADMS,
    VCARD,
    SKOS,
)


# schemingdcat profiles (not ckanext-dcat euro_dcat_ap_*)
DCAT_AP_2_PROFILES = ["eu_dcat_ap_2"]
ES_DCAT_AP_2_PROFILES = ["es_dcat_ap_2"]
DCAT_AP_3_PROFILES = ["eu_dcat_ap_3"]


def _access_service(**overrides):
    service = {
        "uri": "https://example.org/services/wfs",
        "title": "Servicio WFS",
        "endpoint_url": ["https://example.org/geoserver/wfs"],
        "endpoint_description": "https://example.org/geoserver/wfs?request=GetCapabilities",
        "serves_dataset": ["https://example.org/dataset/test-dataset"],
    }
    service.update(overrides)
    return service


def _dataset(**overrides):
    dataset = {
        "id": "4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6",
        "name": "test-dataset",
        "title": "Test DCAT dataset",
        "notes": "Lorem ipsum",
        "identifier": "xx-some-dataset-id-yy",
        "alternate_identifier": ["alt-id-1", "alt-id-2"],
        "contact_name": "Dataset Contact",
        "contact_email": "dataset@example.org",
        "contact_url": "https://example.org/contact",
        "resources": [
            {
                "id": "7fffe9b2-7a24-4d43-91f7-8bd58bad9615",
                "url": "http://example.org/data.csv",
                "name": "Resource 1",
                "access_services": [_access_service()],
            }
        ],
    }
    dataset.update(overrides)
    return dataset


class TestDataServiceVCardAndAdmsIdentifier(BaseSerializeTest):
    """Focused RDF serialization tests for issue #151 (no nested vCard)."""

    def _serialize(self, dataset, profiles=None):
        s = RDFSerializer(profiles=profiles or DCAT_AP_2_PROFILES)
        dataset_ref = s.graph_from_dataset(dataset)
        return s.g, dataset_ref

    def _service_ref(self, g, dataset_ref):
        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        access_services = [
            t for t in g.triples((distribution_ref, DCAT.accessService, None))
        ]
        assert access_services, "expected dcat:accessService on the distribution"
        return access_services[0][2]

    def test_dataservice_own_vcard_from_flat_fields(self):
        dataset = _dataset(
            resources=[
                {
                    "id": "7fffe9b2-7a24-4d43-91f7-8bd58bad9615",
                    "url": "http://example.org/data.csv",
                    "name": "Resource 1",
                    "access_services": [
                        _access_service(
                            contact_name="Service Contact",
                            contact_email="service@example.org",
                            contact_url="https://example.org/service-contact",
                        )
                    ],
                }
            ]
        )
        g, dataset_ref = self._serialize(dataset)
        service_ref = self._service_ref(g, dataset_ref)

        dataset_cp = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        service_cp = self._triple(g, service_ref, DCAT.contactPoint, None)[2]
        assert service_cp != dataset_cp

        assert self._triple(g, service_cp, RDF.type, VCARD.Kind)
        assert self._triple(g, service_cp, VCARD.fn, "Service Contact")
        assert self._triple(
            g, service_cp, VCARD.hasEmail, URIRef("mailto:service@example.org")
        )
        assert self._triple(
            g, service_cp, VCARD.hasURL, URIRef("https://example.org/service-contact")
        )

    def test_dataservice_contactpoint_falls_back_to_dataset(self):
        g, dataset_ref = self._serialize(_dataset())
        service_ref = self._service_ref(g, dataset_ref)

        dataset_cp = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        service_contacts = [
            t[2] for t in g.triples((service_ref, DCAT.contactPoint, None))
        ]
        assert dataset_cp in service_contacts
        assert self._triple(g, dataset_cp, VCARD.fn, "Dataset Contact")

    def test_empty_service_contact_fields_still_fallback(self):
        dataset = _dataset(
            resources=[
                {
                    "id": "7fffe9b2-7a24-4d43-91f7-8bd58bad9615",
                    "url": "http://example.org/data.csv",
                    "name": "Resource 1",
                    "access_services": [
                        _access_service(
                            contact_name="  ",
                            contact_email="",
                            contact_url=None,
                        )
                    ],
                }
            ]
        )
        g, dataset_ref = self._serialize(dataset)
        service_ref = self._service_ref(g, dataset_ref)
        dataset_cp = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        service_contacts = [
            t[2] for t in g.triples((service_ref, DCAT.contactPoint, None))
        ]
        assert dataset_cp in service_contacts

    def test_adms_identifier_one_notation_per_node(self):
        g, dataset_ref = self._serialize(_dataset())

        identifier_nodes = [
            t[2] for t in g.triples((dataset_ref, ADMS.identifier, None))
        ]
        assert len(identifier_nodes) == 2

        notations = []
        for node in identifier_nodes:
            assert self._triple(g, node, RDF.type, ADMS.Identifier)
            node_notations = list(g.objects(node, SKOS.notation))
            assert len(node_notations) == 1
            notations.append(str(node_notations[0]))
            # Identifier node must not carry dct:identifier extras
            assert list(g.objects(node, DCT.identifier)) == []

        assert sorted(notations) == ["alt-id-1", "alt-id-2"]

        dct_ids = [str(o) for o in g.objects(dataset_ref, DCT.identifier)]
        assert "xx-some-dataset-id-yy" in dct_ids
        assert "alt-id-1" not in dct_ids
        assert "alt-id-2" not in dct_ids

    @pytest.mark.parametrize("profiles", [DCAT_AP_2_PROFILES, DCAT_AP_3_PROFILES])
    def test_adms_identifier_pattern_across_profiles(self, profiles):
        g, dataset_ref = self._serialize(_dataset(), profiles=profiles)
        identifier_nodes = [
            t[2] for t in g.triples((dataset_ref, ADMS.identifier, None))
        ]
        assert len(identifier_nodes) == 2
        for node in identifier_nodes:
            assert len(list(g.objects(node, SKOS.notation))) == 1

    def test_dataservice_adms_identifier(self):
        dataset = _dataset(
            resources=[
                {
                    "id": "7fffe9b2-7a24-4d43-91f7-8bd58bad9615",
                    "url": "http://example.org/data.csv",
                    "name": "Resource 1",
                    "access_services": [
                        _access_service(identifier="ES-service-wfs-001")
                    ],
                }
            ]
        )
        g, dataset_ref = self._serialize(dataset)
        service_ref = self._service_ref(g, dataset_ref)

        service_ids = [t[2] for t in g.triples((service_ref, ADMS.identifier, None))]
        assert len(service_ids) == 1
        assert self._triple(g, service_ids[0], RDF.type, ADMS.Identifier)
        assert self._triple(g, service_ids[0], SKOS.notation, "ES-service-wfs-001")
        assert list(g.objects(service_ids[0], DCT.identifier)) == []
        # Dataset dct:identifier remains the primary dataset id only
        dct_ids = [str(o) for o in g.objects(dataset_ref, DCT.identifier)]
        assert "ES-service-wfs-001" not in dct_ids
