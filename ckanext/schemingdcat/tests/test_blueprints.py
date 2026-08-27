# -*- coding: utf-8 -*-
import pytest
from ckan.plugins.toolkit import url_for
from ckan.tests import factories


# Required DCAT fields from the default test.ini schema
# (schemas/geodcat_ap/es_geodcat_ap_full.yaml)
_REQUIRED_DCAT_FIELDS = {
    "contact_email": "contact@example.org",
    "dcat_type": "http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset",
    "identifier": "test-blueprint-dataset-identifier",
    "language": "http://publications.europa.eu/resource/authority/language/ENG",
    "topic": "http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/location",
    "theme_es": [
        "http://datos.gob.es/kos/sector-publico/sector/ciencia-tecnologia"
    ],
    "private": False,
}


def _dcat_dataset(**kwargs):
    """Create a dataset that satisfies required DCAT/GeoDCAT schema fields."""
    data = dict(_REQUIRED_DCAT_FIELDS)
    data.update(kwargs)
    return factories.Dataset(**data)


def _build_url(app, endpoint, **kwargs):
    try:
        return url_for(endpoint, **kwargs)
    except RuntimeError:
        flask_app = getattr(app, "flask_app", None) or app.app
        with flask_app.test_request_context():
            return url_for(endpoint, **kwargs)


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index')
class TestSchemingDCATBlueprints:

    def test_endpoints(self, app):
        url = _build_url(app, 'schemingdcat.endpoint_index')
        response = app.get(url)
        assert response.status_code == 200
        assert 'endpoints' in response.body

    def test_metadata_templates(self, app):
        url = _build_url(app, 'schemingdcat.metadata_templates')
        response = app.get(url)
        assert response.status_code == 200
        assert 'Metadata templates' in response.body

    def test_linked_data(self, app):
        dataset = _dcat_dataset()
        response = app.get('/dataset/linked_data/{}'.format(dataset['name']))
        assert response.status_code == 200
        assert 'Custom Data' in response.body

    def test_geospatial_metadata(self, app):
        dataset = _dcat_dataset()
        response = app.get(
            '/dataset/geospatial_metadata/{}'.format(dataset['name'])
        )
        assert response.status_code == 200
        assert 'Custom Data' in response.body

    def test_linked_data_not_found(self, app):
        response = app.get('/dataset/linked_data/nonexistent-id', status=404)
        assert response.status_code == 404

    def test_geospatial_metadata_not_found(self, app):
        response = app.get(
            '/dataset/geospatial_metadata/nonexistent-id', status=404
        )
        assert response.status_code == 404
