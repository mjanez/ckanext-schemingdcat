import re
import logging
import json

from rdflib import term, URIRef, Literal

from ckantoolkit import config, get_action

from ckanext.dcat.profiles.base import RDFProfile, URIRefOrLiteral, CleanedURIRef

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
    "dc": DC,
    "dct": DCT,
    "dcat": DCAT,
    "dcatap": DCATAP,
    "adms": ADMS,
    "vcard": VCARD,
    "foaf": FOAF,
    "schema": SCHEMA,
    "time": TIME,
    "skos": SKOS,
    "locn": LOCN,
    "gsp": GSP,
    "owl": OWL,
    "cnt": CNT,
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
    
    # Add multilang to methods
    def _object_value(self, subject, predicate, multilang=False):
        """
        Given a subject and a predicate, returns the value of the object

        Both subject and predicate must be rdflib URIRef or BNode objects

        If found, the string representation is returned, else an empty string
        """
        lang_dict = {}
        fallback = ""
                
        for o in self.g.objects(subject, predicate):
            if isinstance(o, Literal):
                if o.language and o.language == default_lang:
                    return str(o)
                if multilang and o.language:
                    lang_dict[o.language] = str(o)
                elif multilang:
                    lang_dict[default_lang] = str(o)
                else:
                    return str(o)
                if multilang:
                    # when translation does not exist, create an empty one
                    for lang in get_langs():
                        if lang not in lang_dict:
                            lang_dict[lang] = ""
                    return lang_dict
                # Use first object as fallback if no object with the default language is available
                elif fallback == "":
                    fallback = str(o)
            else:
                return str(o)
        return fallback
    
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
        Returns a dict with details about a vcard expression

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

        {
            'uri': 'http://orgs.vocab.org/some-org',
            'name': 'Contact Point for dataset 1',
            'email': 'contact@some.org',
            'url': 'http://some.org',
            'role': 'pointOfContact',
        }

        Returns keys for uri, name, email and url with the values set to
        an empty string if they could not be found
        """

        contact = {}

        for agent in self.g.objects(subject, predicate):

            contact["uri"] = str(agent) if isinstance(agent, term.URIRef) else ""

            contact["name"] = self._get_vcard_property_value(
                agent, VCARD.hasFN, VCARD.fn
            )

            contact["url"] = self._get_vcard_property_value(
                agent, VCARD.hasURL
            )

            contact["role"] = self._get_vcard_property_value(
                agent, VCARD.role
            )

            contact["email"] = self._without_mailto(
                self._get_vcard_property_value(agent, VCARD.hasEmail)
            )

        return contact
    
    def _author(self, subject, predicate):
        """
        Returns a dict with details about a dct:creator entity, a foaf:Person

        Both subject and predicate must be rdflib URIRef or BNode objects

        Examples:

        <dct:creator>
            <foaf:Person rdf:about="http://people.vocab.org/some-person">
                <foaf:name>Author Name</foaf:name>
                <foaf:mbox>author@some.org</foaf:mbox>
                <foaf:homepage>http://author.org</foaf:homepage>
            </foaf:Person>
        </dct:creator>

        {
            'uri': 'http://people.vocab.org/some-person',
            'name': 'Author Name',
            'email': 'author@some.org',
            'url': 'http://author.org',
        }

        <dct:creator rdf:resource="http://people.vocab.org/another-person" />

        {
            'uri': 'http://people.vocab.org/another-person'
        }

        Returns keys for uri, name, email, url, and identifier with the values set to
        an empty string if they could not be found
        """

        author = {}

        for person in self.g.objects(subject, predicate):

            author["uri"] = str(person) if isinstance(person, term.URIRef) else ""

            author["name"] = self._object_value(person, FOAF.name)

            author["email"] = self._object_value(person, FOAF.mbox)

            author["url"] = self._object_value(person, FOAF.homepage)

        return author
    
    # ckanext-schemingdcat: codelists functions
    def _search_values_codelist_add_to_graph(self, metadata_codelist, labels, dataset_dict, dataset_ref, dataset_tag_base, g, dcat_property):
        # Create a dictionary with label as key and id as value for each element in metadata_codelist
        inspire_dict = {row["label"].lower(): row.get("id", row.get("value")) for row in metadata_codelist}
        
        # Check if labels is a list, if not, convert it to a list
        if not isinstance(labels, list):
            labels = [labels]
        
        for label in labels:
            if label not in self._get_dataset_value(dataset_dict, "topic"):
                # Check if tag_name is in inspire_dict
                if label.lower() in inspire_dict:
                    tag_val = inspire_dict[label.lower()]
                else:
                    tag_val = f"{dataset_tag_base}/dataset/?tags={label}"
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
        
    # Multilang management
    def _add_date_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items,
                                    date_value=True)

    def _add_list_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items,
                                    list_value=True)

    def _add_triples_from_dict(
        self, _dict, subject, items, list_value=False, date_value=False, multilang=False
    ):
        for item in items:
            try:
                if len(item) == 4:
                    key, predicate, fallbacks, _type = item
                    _class = None
                    required_lang = None
                elif len(item) == 5:
                    key, predicate, fallbacks, _type, _class = item
                    required_lang = None
                elif len(item) == 6:
                    key, predicate, fallbacks, _type, _class, required_lang = item
            except ValueError:
                key, predicate, fallbacks, _type = item
                _class = None
                required_lang = None

            self._add_triple_from_dict(
                _dict,
                subject,
                predicate,
                key,
                fallbacks=fallbacks,
                list_value=list_value,
                date_value=date_value,
                _type=_type,
                _class=_class,
                multilang=multilang,
                required_lang=required_lang,
            )

    def _add_triple_from_dict(
        self,
        _dict,
        subject,
        predicate,
        key,
        fallbacks=None,
        list_value=False,
        date_value=False,
        _type=Literal,
        _datatype=None,
        _class=None,
        value_modifier=None,
        multilang=False,
        required_lang= None,
    ):
        """
        Adds a new triple to the graph with the provided parameters

        The subject and predicate of the triple are passed as the relevant
        RDFLib objects (URIRef or BNode). As default, the object is a
        literal value, which is extracted from the dict using the provided key
        (see `_get_dict_value`). If the value for the key is not found, then
        additional fallback keys are checked.
        Using `value_modifier`, a function taking the extracted value and
        returning a modified value can be passed.
        If a value was found, the modifier is applied before adding the value.

        `_class` is the optional RDF class of the entity being added.

        If `list_value` or `date_value` are True, then the value is treated as
        a list or a date respectively (see `_add_list_triple` and
        `_add_date_triple` for details.
        """        
        value = self._get_dict_value(_dict, key)
        if not value and fallbacks:
            for fallback in fallbacks:
                value = self._get_dict_value(_dict, fallback)
                if value:
                    break

        # if a modifying function was given, apply it to the value
        if value and callable(value_modifier):
            value = value_modifier(value)

        if value and list_value:
            self._add_list_triple(subject, predicate, value, _type, _datatype, _class)
        elif value and date_value:
            self._add_date_triple(subject, predicate, value, _type)
        # if multilang is True, the value is a dict with language codes as keys
        elif value and multilang:
            self._add_multilang_triple(subject, predicate, value, required_lang)
        elif value:
            # Normal text value
            # ensure URIRef items are preprocessed (space removal/url encoding)
            if _type == URIRef:
                _type = CleanedURIRef
            if _datatype:
                object = _type(value, datatype=_datatype)
            else:
                object = _type(value)
            self.g.add((subject, predicate, object))

            if _class and isinstance(object, URIRef):
                self.g.add((object, RDF.type, _class))

    # mjanez/ckanext-dcat. Multilang triples.
    def _add_multilang_triple(self, subject, predicate, multilang_values, required_lang=None):
        """
        Adds multilingual triples to the graph.

        This method processes the provided `multilang_values`, which can be a string,
        dictionary, or any other value, and adds them to the RDF graph with the specified
        language tags. If `required_lang` is provided, only values with the matching
        language code are added.

        Args:
            subject (URIRef or BNode): The subject of the RDF triple.
            predicate (URIRef): The predicate of the RDF triple.
            multilang_values (Union[str, dict, Any]): The multilingual values to be added.
                This can be a JSON string, a dictionary with language codes as keys, or any other value.
            required_lang (Optional[str]): The required language code. Only values with this
                language code are added. If None, all values are added.

        Returns:
            None
        """
        # log.debug("subject: {1} and multilang_values: {0}".format(multilang_values, subject))
        # log.debug("required_lang: %s and multilang_values type: %s", required_lang, str(type(multilang_values)))

        if not multilang_values:
            return

        if isinstance(multilang_values, str):
            try:
                multilang_values = json.loads(multilang_values)
            except ValueError:
                pass

        if isinstance(multilang_values, dict):
            try:
                for key, value in multilang_values.items():
                    if value and value != "":
                        self.g.add((subject, predicate, Literal(value, lang=key)))
            except (ValueError, KeyError):
                self.g.add((subject, predicate, Literal(multilang_values)))

        else:
            self.g.add((subject, predicate, Literal(multilang_values)))
            
    # Catalog class enhancements
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