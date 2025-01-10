import re
import logging
import json
from urllib.parse import quote

from rdflib import term, URIRef, Literal

from ckantoolkit import config, get_action, aslist
from ckan.lib.helpers import is_url

from ckanext.dcat.profiles.base import RDFProfile, URIRefOrLiteral, CleanedURIRef, DEFAULT_SPATIAL_FORMATS, GEOJSON_IMT, InvalidGeoJSONException, wkt
from ckanext.schemingdcat.config import (
    translate_validator_tags
)

from ckanext.schemingdcat.helpers import get_langs
from ckanext.schemingdcat.codelists import load_inspire_csv_codelists
from ckanext.schemingdcat.profiles.dcat_config import (
    # Vocabs
    RDF,
    RDFS,
    SKOS,
    ELI,
    EUROVOC,
    DCAT,
    DC,
    DCT,
    DCAT,
    DCATAP,
    GEODCATAP,
    DCATUS,
    ADMS,
    VCARD,
    FOAF,
    SCHEMA,
    TIME,
    LOCN,
    GSP,
    OWL,
    SPDX,
    CNT,
    ORG,
    # Default values
    eu_dcat_ap_default_values,
    )

# INSPIRE Codelists
codelists = load_inspire_csv_codelists()
MD_INSPIRE_REGISTER = codelists["MD_INSPIRE_REGISTER"]
MD_FORMAT = codelists["MD_FORMAT"]
MD_ES_THEMES = codelists["MD_ES_THEMES"]
MD_EU_THEMES = codelists["MD_EU_THEMES"]
MD_EU_LANGUAGES = codelists["MD_EU_LANGUAGES"]
MD_ES_FORMATS = codelists["MD_ES_FORMATS"]

namespaces = {
    "cnt": CNT,
    "dc": DC,
    "dct": DCT,
    "dcat": DCAT,
    "dcatap": DCATAP,
    "geodcatap": GEODCATAP,
    "eli": ELI,
    "dcatus": DCATUS,
    "adms": ADMS,
    "vcard": VCARD,
    "foaf": FOAF,
    "schema": SCHEMA,
    "time": TIME,
    "skos": SKOS,
    "locn": LOCN,
    "gsp": GSP,
    "owl": OWL,
    "org": ORG,
    "spdx": SPDX,
}

default_lang = config.get("ckan.locale_default", "en")

log = logging.getLogger(__name__)


class SchemingDCATRDFProfile(RDFProfile):
    """
    A custom ckanext-dcat Base RDF Profile for the ckanext-schemingdcat extension. https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/profiles/base.py

    Notes:
        **RDFProfile**: Base class with helper methods for implementing RDF parsing profiles

        This class should not be used directly, but rather extended to create
        custom profiles

    """
    
    # ckanext-schemingdcat profiles: INSPIRE/DCAT Themes.
    def _themes(self, dataset_ref):
        """
        Returns all DCAT themes on a particular dataset
        """
        # Precompile regular expressions for faster matching
        data_es_pattern = re.compile(r"https?://datos\.gob\.es/")
        inspire_eu_pattern = re.compile(r"https?://inspire\.ec\.europa\.eu/theme")
        themes = set()

        for theme in self._object_value_list(dataset_ref, DCAT.theme):
            theme = theme.replace("https://", "http://")

            if data_es_pattern.match(theme):
                themes.add(theme)
                if theme:
                    theme_es_dcat_ap = self._search_value_codelist(MD_ES_THEMES, theme, "id","dcat_ap") or None
                    themes.add(theme_es_dcat_ap)
                
            elif inspire_eu_pattern.match(theme):
                themes.add(theme)
                if theme:
                    theme_eu_dcat_ap = self._search_value_codelist(MD_EU_THEMES, theme, "id","dcat_ap") or None
                    themes.add(theme_eu_dcat_ap)

        return themes
    
    
    # Improve publisher/contact details
    def _publisher(self, subject, predicate):
        """
        Returns a dict with details about a dct:publisher entity, a foaf:Agent

        Both subject and predicate must be rdflib URIRef or BNode objects

        Examples:

        <dct:publisher>
            <foaf:Organization rdf:about="http://orgs.vocab.org/some-org">
                <foaf:name>Publishing Organization for dataset 1</foaf:name>
                <foaf:mbox>contact@some.org</foaf:mbox>
                <foaf:homepage>http://some.org</foaf:homepage>
                <dct:type rdf:resource="http://purl.org/adms/publishertype/NonProfitOrganisation"/>
                <dct:identifier>EA349s92</dct:identifier>
            </foaf:Organization>
        </dct:publisher>

        {
            'uri': 'http://orgs.vocab.org/some-org',
            'name': 'Publishing Organization for dataset 1',
            'email': 'contact@some.org',
            'url': 'http://some.org',
            'type': 'http://purl.org/adms/publishertype/NonProfitOrganisation',
            'identifier': 'EA349s92'
        }

        <dct:publisher rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/EURCOU" />

        {
            'uri': 'http://publications.europa.eu/resource/authority/corporate-body/EURCOU'
        }

        Returns keys for uri, name, email, url and type with the values set to
        an empty string if they could not be found
        """

        publisher = {}

        for agent in self.g.objects(subject, predicate):

            publisher["uri"] = str(agent) if isinstance(agent, term.URIRef) else ""

            publisher["name"] = self._object_value(agent, FOAF.name)

            publisher["email"] = self._object_value(agent, FOAF.mbox)

            publisher["url"] = self._object_value(agent, FOAF.homepage)

            publisher["type"] = self._object_value(agent, DCT.type)

            publisher["identifier"] = self._object_value(agent, DCT.identifier)

        return publisher

    def _contact_details(self, subject, predicate):
        """
        Returns a list of dicts with details about vcard expressions

        Both subject and predicate must be rdflib URIRef or BNode objects

        Examples:

        <dcat:contactPoint>
            <vcard:Organization rdf:nodeID="Nc320885686e84382a0a2ea602ebde399">
                <vcard:fn>Contact Point for dataset 1</vcard:fn>
                <vcard:hasEmail <mailto:contact@some.org>
                <vcard:hasURL>http://some.org<vcard:hasURL>
                <vcard:role>pointOfContact<vcard:role>
            </vcard:Organization>
        </dcat:contactPoint>

        [
            {
            'uri': 'http://orgs.vocab.org/some-org',
            'name': 'Contact Point for dataset 1',
            'email': 'contact@some.org',
            'url': 'http://some.org',
            'role': 'pointOfContact',
            }
        ]

        Returns keys for uri, name, email and url with the values set to
        an empty string if they could not be found
        """

        contacts = []

        for agent in self.g.objects(subject, predicate):

            contact = {}                
            contact["uri"] = str(agent) if isinstance(agent, URIRef) else ""

            contact["name"] = self._get_vcard_property_value(
                agent, VCARD.hasFN, VCARD.fn
            )

            contact["email"] = self._without_mailto(
                self._get_vcard_property_value(agent, VCARD.hasEmail)
            )

            contact["identifier"] = self._get_vcard_property_value(agent, VCARD.hasUID)

            contact["url"] = self._get_vcard_property_value(
                agent, VCARD.hasURL
            )

            contact["role"] = self._get_vcard_property_value(
                agent, VCARD.role
            )

            contacts.append(contact)

        return contacts
        
    # ckanext-schemingdcat: Multilang management
    ## Since  ckanext-dcat v2.1.0 unnecessary due to its multilingual support ##
    
    #TODO: Delete deprecated method
    def _get_localized_dataset_value(self, multilang_dict, default=None):
        """Returns a localized dataset multilang_dict.

        Args:
            multilang_dict: A string or dictionary representing the multilang_dict to localize.
            default: A default value to return if the multilang_dict cannot be localized.

        Returns:
            A dictionary representing the localized multilang_dict, or the default value if the multilang_dict cannot be localized.

        Raises:
            None.
        """
        if isinstance(multilang_dict, dict):
            return multilang_dict

        if isinstance(multilang_dict, str):
            try:
                multilang_dict = json.loads(multilang_dict)
            except ValueError:
                return default
    
    # ckanext-schemingdcat: Catalog class enhancements
    def _get_catalog_field(self, field_name, default_values_dict=eu_dcat_ap_default_values, fallback=None, return_none=False, order="desc"):
        """
        Returns the value of a field from the most recently modified dataset.

        Args:
            field_name (str): The name of the field to retrieve from datasets list
            default_values_dict (dict): A dictionary of default values to use if the field is not found. Defaults to eu_dcat_ap_default_values.
            fallback (str): The name of the fallback field to retrieve if `field_name` is not found. Defaults to None.
            return_none (bool): Whether to return None if the field is not found. Defaults to False.
            order (str): The order in which to sort the results. Defaults to "desc".

        Returns:
            The value of the field, or the default value if it could not be found and `return_none` is False.

        Notes:
            This function caches the result of the CKAN API call to improve performance. The cache is stored in the `_catalog_search_result` attribute of the object. If the attribute exists, the function will return the value of the requested field from the cached result instead of making a new API call. If the attribute does not exist, the function will make a new API call and store the result in the attribute for future use.
        """
        if not hasattr(self, "_catalog_search_result"):
            context = {
                "ignore_auth": True
            }
            self._catalog_search_result = get_action("package_search")(context, {
                "sort": f"metadata_modified {order}",
                "rows": 1,
            })
        try:
            if self._catalog_search_result and self._catalog_search_result.get("results"):
                return self._catalog_search_result["results"][0][field_name]
        except KeyError:
            pass
        if fallback:
            try:
                if self._catalog_search_result and self._catalog_search_result.get("results"):
                    return self._catalog_search_result["results"][0][fallback]
            except KeyError:
                pass
        if return_none:
            return None
        return default_values_dict[field_name]

    def _get_catalog_dcat_theme(self):
        """
        Returns the value of the `theme_es` field from the most recently created dataset,
        or the value of the `theme_eu` field if `theme_es` is not present.

        Returns None if neither `theme_es` nor `theme_eu` are present in the dataset.

        Returns:
            A string with the value of the `theme_es` or `theme_eu` field, or None if not found.
        """
        context = {
            "ignore_auth": True
        }
        result = get_action("package_search")(context, {
            "sort": "metadata_created desc",
            "rows": 1,
        })
        if result and result.get("results"):
            if "theme_es" in result["results"][0]:
                return result["results"][0]["theme_es"][0]
            elif "theme_eu" in result["results"][0]:
                return result["results"][0]["theme_eu"][0]
        return None

    def _get_catalog_language(self, default_values=eu_dcat_ap_default_values):
        """
        Returns the value of the `language` field from the most recently modified dataset.

        Args:
            default_values (dict): A dictionary of default values to use if the `publisher_uri` field cannot be found.

        Returns:
            A string with the value of the `language` field, or None if it could not be found.
        """
        context = {
            "ignore_auth": True
        }
        result = get_action("package_search")(context, {
            "sort": "metadata_modified desc",
            "rows": 1,
        })
        try:
            if result and result.get("results"):
                return result["results"][0]["language"]
            
        except KeyError:
            return default_values["language"]

    # ckanext-schemingdcat: Codelist management
    def _search_values_codelist_add_to_graph(self, metadata_codelist, labels, dataset_dict, dataset_ref, dataset_tag_base, g, dcat_property, lang=None):
        """
        Adds values from a metadata codelist to a graph based on provided labels.
    
        Args:
            metadata_codelist (list): A list of dictionaries containing metadata codelist entries.
            labels (list or str): A list of labels or a single label to search for in the codelist.
            dataset_dict (dict): The dataset dictionary containing dataset metadata.
            dataset_ref (URIRef): The reference URI of the dataset.
            dataset_tag_base (str): The base URL for dataset tags.
            g (Graph): The RDF graph to which the values will be added.
            dcat_property (URIRef): The DCAT property to be used for adding values to the graph.
            lang (str, optional): The language of the labels. Defaults to None.
    
        """
        # Create a dictionary with label as key and id as value for each element in metadata_codelist
        inspire_dict = {row["label"].lower(): row.get("id", row.get("value")) for row in metadata_codelist}
        
        # Ensure labels is a list
        if not isinstance(labels, list):
            labels = [labels]
        
        # Get 'topic' from dataset_dict, handle NoneType
        topics = self._get_dataset_value(dataset_dict, "topic")
        if not topics:
            topics = []
        elif not isinstance(topics, list):
            topics = [topics]
        
        for label in labels:
            if label not in topics:
                # Check if label is in inspire_dict
                if label.lower() in inspire_dict:
                    tag_val = inspire_dict[label.lower()]
                else:
                    tag_val = f"{dataset_tag_base}/dataset/?tags={label}"
                    
                if lang:
                    g.add((dataset_ref, dcat_property, Literal(tag_val, lang=lang)))
                else:
                    g.add((dataset_ref, dcat_property, URIRefOrLiteral(tag_val)))

    def dict_to_list(self, value):
        """Converts a dictionary to a list of its values.

        Args:
            value: The value to convert.

        Returns:
            If the value is a dictionary, returns a list of its values. Otherwise, returns the value unchanged.
        """
        if isinstance(value, dict):
            value = list(value.values())
        return value

    def _search_value_codelist(self, metadata_codelist, label, input_field_name, output_field_name, return_value=True):
        """Searches for a value in a metadata codelist.

        Args:
            metadata_codelist (list): A list of dictionaries containing the metadata codelist.
            label (str): The label to search for in the codelist.
            input_field_name (str): The name of the input field in the codelist.
            output_field_name (str): The name of the output field in the codelist.
            return_value (bool): Whether to return the label value if not found (True) or None if not found (False). Default is True.

        Returns:
            str or None: The value found in the codelist, or None if not found and return_value is False.
        """
        inspire_dict = {row[input_field_name].lower(): row[output_field_name] for row in metadata_codelist}
        tag_val = inspire_dict.get(label.lower(), None)
        if not return_value and tag_val is None:
            return None
        elif not return_value and tag_val:
            return tag_val        
        elif return_value == True and tag_val is None:
            return label
        else:
            return tag_val

    # ckanext-dcat fixes
    ## https://github.com/mjanez/ckanext-dcat/issues/4
    def _add_spatial_value_to_graph(self, spatial_ref, predicate, value):
        """
        Adds spatial triples to the graph. Assumes that value is a GeoJSON string
        or object.
        """
        spatial_formats = aslist(
            config.get(
                "ckanext.dcat.output_spatial_format", DEFAULT_SPATIAL_FORMATS
            )
        )
    
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                return

        # Check if the predicate already exists for the spatial_ref. Location props have only one (0..1).
        if (spatial_ref, predicate, None) in self.g:
            return
    
        if "wkt" in spatial_formats:
            # WKT, because GeoDCAT-AP says so
            try:
                self.g.add(
                    (
                        spatial_ref,
                        predicate,
                        Literal(
                            wkt.dumps(value, decimals=4),
                            datatype=GSP.wktLiteral,
                        ),
                    )
                )
            except (TypeError, ValueError, InvalidGeoJSONException):
                pass
    
        if "geojson" in spatial_formats:
            # GeoJSON
            self.g.add((spatial_ref, predicate, Literal(json.dumps(value), datatype=GEOJSON_IMT)))
            
    # ckanext-dcat enhancements
    def _multilingual_fields(self, entity="dataset"):
        """
        Retrieve multilingual fields from the dataset schema.
    
        This function checks the dataset schema for fields that have validators
        indicating they are multilingual. It looks for validators that start with
        any of the tags specified in `translate_validator_tags`.
    
        Args:
            entity (str, optional): The entity type to check for multilingual fields.
                                    Defaults to "dataset".
    
        Returns:
            list: A list of fields that are considered multilingual.
        """    
        if not self._dataset_schema:
            return []
    
        out = []
        for field in self._dataset_schema[f"{entity}_fields"]:
            if field.get("validators") and any(
                v for v in field["validators"].split() if any(tag for tag in translate_validator_tags if v.startswith(tag))
            ):
                out.append(field["field_name"])
        return out
    
    def _publisher_fallback_details(self, dataset_dict):
        """
        Use contact details for publisher if not already set.
    
        This method checks if the publisher details (name, email, url, identifier, uri)
        are present in the dataset_dict or dataset_dict["extras"]. If they are not present,
        it uses the corresponding contact details to fill in the publisher details.
    
        Args:
            dataset_dict (dict): The dataset dictionary containing metadata fields.
    
        Returns:
            None
        """
        contact_keys = ["name", "email", "url", "identifier", "uri"]
        for key in contact_keys:
            contact_key = f"contact_{key}"
            publisher_key = f"publisher_{key}"
            if not any(extra['key'] == publisher_key for extra in dataset_dict["extras"]) and publisher_key not in dataset_dict:
                if contact_key in dataset_dict:
                    dataset_dict["extras"].append(
                        {
                            "key": publisher_key,
                            "value": dataset_dict[contact_key]
                        }
                    )
                    dataset_dict[publisher_key] = dataset_dict[contact_key]

    def _add_valid_url_to_graph(self, graph, subject, predicate, url, fallback_url):
        """
        Add a valid URL to the graph. If the URL is not valid, use the fallback URL.
        
        Args:
            graph (rdflib.Graph): The RDF graph.
            subject (rdflib.term.URIRef): The subject of the triple.
            predicate (rdflib.term.URIRef): The predicate of the triple.
            url (str): The URL to validate and add.
            fallback_url (str): The fallback URL to use if the URL is not valid.
        """
        if isinstance(url, str):
            encoded_url = quote(url, safe=':/?&=')
            valid_url = URIRef(encoded_url) if is_url(encoded_url) else None
            if valid_url:
                graph.add((subject, predicate, valid_url))
            elif fallback_url and isinstance(fallback_url, str):
                encoded_fallback_url = quote(fallback_url, safe=':/?&=')
                graph.add((subject, predicate, URIRef(encoded_fallback_url)))

    def _is_direct_download_url(self, url):
        """
        Check if the URL is a direct download link.
    
        Args:
            url (str): The URL to check.
    
        Returns:
            bool: True if the URL is a direct download link, False otherwise.
        """
        # Check if the URL ends with '/download' or with an extension like '.ext'
        if url.endswith('/download'):
            return True
        
        # Check if the URL ends with a common file extension
        if '.' in url.split('/')[-1]:
            return True
        
        # Additional checks for common download patterns
        common_download_patterns = ['/files/', '/downloads/', '/get/', '/dl/']
        for pattern in common_download_patterns:
            if pattern in url:
                return True
        
        return False