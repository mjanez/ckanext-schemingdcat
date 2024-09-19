from click.testing import CliRunner
from ckanext.schemingdcat.cli import schemingdcat


def test_create_inspire_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["create-inspire-tags", "-l", "en"])
    assert result.exit_code == 0
    assert "Creating 'inspire_themes' CKAN tag vocabulary" in result.output


def test_delete_inspire_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["delete-inspire-tags"])
    assert result.exit_code == 0
    assert "Deleting inspire_themes CKAN tag vocabulary" in result.output


def test_create_dcat_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["create-dcat-tags", "-l", "en"])
    assert result.exit_code == 0
    assert "Creating 'dcat_ap' CKAN tag vocabulary" in result.output


def test_delete_dcat_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["delete-dcat-tags"])
    assert result.exit_code == 0
    assert "Deleting dcat_ap CKAN tag vocabulary" in result.output


def test_create_iso_topic_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["create-iso-topic-tags", "-l", "en"])
    assert result.exit_code == 0
    assert "Creating 'iso19115_topics' CKAN tag vocabulary" in result.output


def test_delete_iso_topic_tags():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["delete-iso-topic-tags"])
    assert result.exit_code == 0
    assert "Deleting iso19115_topics CKAN tag vocabulary" in result.output


def test_download_rdf_eu_vocabs():
    runner = CliRunner()
    result = runner.invoke(schemingdcat, ["download-rdf-eu-vocabs"])
    assert result.exit_code == 0
    assert "Downloading EU Vocabularies..." in result.output