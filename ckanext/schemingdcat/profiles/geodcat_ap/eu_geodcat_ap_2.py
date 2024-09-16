import json
import logging
from decimal import Decimal, DecimalException

from rdflib import URIRef, BNode, Literal

from ckanext.dcat.utils import resource_uri
from ckanext.dcat.profiles.base import URIRefOrLiteral, CleanedURIRef

from ckanext.schemingdcat.profiles.base import (
    # Codelists
    MD_INSPIRE_REGISTER,
    MD_FORMAT,
    MD_EU_LANGUAGES,
)

from ckanext.schemingdcat.profiles.dcat_ap.eu_dcat_ap_2 import EuDCATAP2Profile
from ckanext.schemingdcat.profiles.dcat_config import (
    # Vocabs
    RDF,
    DCAT,
    DCATAP,
    GEODCATAP,
    VCARD,
    DCT,
    XSD,
    SCHEMA,
    RDFS,
    ADMS,
    CNT,
    ELI,
    # Default values
    metadata_field_names,
    eu_geodcat_ap_default_values,
    )


log = logging.getLogger(__name__)

#TODO: Implement GeoDCAT-AP 2 profile
class EuGeoDCATAP2Profile(EuDCATAP2Profile):
    """
    A custom RDF profile based on the GeoDCAT-AP 2 for data portals in Europe

    More information and specification:

    https://joinup.ec.europa.eu/collection/semic-support-centre/solution/geodcat-application-profile-data-portals-europe

    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        dataset_dict = self._parse_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        dataset_dict = self._parse_dataset_v2(dataset_dict, dataset_ref)

        # GeoDCAT-AP 2 properties
        dataset_dict = self._parse_dataset_geodcat_ap_v2(dataset_dict, dataset_ref)

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        self._graph_from_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        self._graph_from_dataset_v2(dataset_dict, dataset_ref)

        # DCAT AP v2 specific properties
        self._graph_from_dataset_v2_only(dataset_dict, dataset_ref)
        
        # GeoDCAT-AP 2 properties
        self._graph_from_dataset_geodcat_ap_v2(dataset_dict, dataset_ref)

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        
        # Call base method for common properties
        self._graph_from_catalog_base(catalog_dict, catalog_ref)
        
        # GeoDCAT-AP 2 Catalog properties
        self._graph_from_catalog_geodcat_ap_v2(catalog_dict, catalog_ref)

    def _parse_dataset_geodcat_ap_v2(self, dataset_dict, dataset_ref):

        # Call base super method for common properties
        super().parse_dataset(dataset_dict, dataset_ref)

        #  Lists
        for key, predicate, in (
            (metadata_field_names["eu_dcat_ap"]["theme"], DCAT.theme),
            (metadata_field_names["es_dcat_ap"]["theme"], DCAT.theme),
            ("metadata_profile", DCT.conformsTo),
            ("inspire_id", ADMS.identifier),
            ("lineage_source", DCT.source),
            ("reference", DCAT.relation),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict["extras"].append({"key": key, "value": json.dumps(values)})

        # Basic fields
        for key, predicate in (
            ("topic", DCAT.keyword, None),
            ("representation_type", ADMS.representionTechnique, None),
        ):
            value = self._object_value(dataset_ref, predicate)
            if value:
                dataset_dict[key] = value

        # Parse roles
        roles = [
            ("contact", [DCAT.contactPoint, ADMS.contactPoint]),
            ("author", [DCT.creator]),
            ("publisher", [DCT.publisher])
        ]

        for role, predicates in roles:
            contact_details = None
            for predicate in predicates:
                contact_details = self._contact_details(dataset_ref, predicate)
                if contact_details:
                    break
            
            if contact_details and contact_details.get("role"):
                dataset_dict["extras"].append(
                    {"key": f"{role}_role", "value": contact_details.get("role")}
                )

        #  Lists
        for key, predicate, in (
            (metadata_field_names["eu_dcat_ap"]["theme"], DCAT.theme),
            (metadata_field_names["es_dcat_ap"]["theme"], DCAT.theme),
            ('inspire_id', ADMS.identifier),
            ('metadata_profile', DCT.conformsTo),
            ('lineage_source', DCT.source),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict["extras"].append({"key": key, "value": json.dumps(values)})

        return dataset_dict

    def _graph_from_dataset_geodcat_ap_v2(self, dataset_dict, dataset_ref):
        """
        CKAN -> DCAT properties carried forward to higher GeoDCAT-AP versions
        """


        # INSPIRE roles. https://semiceu.github.io/GeoDCAT-AP/releases/3.0.0#responsible-party-and-metadata-point-of-contact---dataset-responsible-party-and-metadata-point-of-contact
        
        # Contact Point
        if any([
            self._get_dataset_value(dataset_dict, "contact_uri"),
            self._get_dataset_value(dataset_dict, "contact_role"),
        ]):
            self._add_role(dataset_dict, "contact_uri", role_key="contact_role")    
    
        # Maintainer
        if self._get_dataset_value(dataset_dict, "maintainer_uri"):
            self._add_role(dataset_dict, "maintainer_uri", role_value=eu_geodcat_ap_default_values["maintainer_role"])

        # Publisher
        if self._get_dataset_value(dataset_dict, "publisher_uri"):
            self._add_role(dataset_dict, "publisher_uri", role_value=eu_geodcat_ap_default_values["publisher_role"])

        # Author
        if self._get_dataset_value(dataset_dict, "author_uri"):
            self._add_role(dataset_dict, "author_uri", role_value=eu_geodcat_ap_default_values["author_role"])

        #  Lists
        items = [
            (metadata_field_names["eu_dcat_ap"]["theme"], DCAT.theme, None, URIRef),
            (metadata_field_names["es_dcat_ap"]["theme"], DCAT.theme, None, URIRef),
            ("metadata_profile", DCT.conformsTo, None, URIRef),
            ("inspire_id", ADMS.identifier, None, URIRefOrLiteral),
            ("lineage_source", DCT.source, None, Literal),
            ("reference", DCAT.relation, None, URIRefOrLiteral),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        # Basic fields without translating fields
        basic_items = [
            ("topic", DCAT.keyword, None, URIRefOrLiteral),
            ("representation_type", ADMS.representionTechnique, None, URIRefOrLiteral),
        ]
        
        # Filtrar los campos básicos para excluir los que ya están en los campos traducidos
        filtered_basic_items = [item for item in basic_items if item[0] not in self._translated_field_names]
        
        self._add_triples_from_dict(dataset_dict, dataset_ref, filtered_basic_items)

    def _graph_from_catalog_geodcat_ap_v2(self, catalog_dict, catalog_ref):
        """
        CKAN -> DCAT Catalog properties carried forward to higher GeoDCAT-AP versions
        """
        pass
    
    def _add_role(self, dataset_dict, uri_key, role_value=None, role_key=None):
        """
        Adds a role to a dataset entity in the graph.

        This function handles the addition of roles to dataset entities. It first
        retrieves the URI from the dataset dictionary using the provided `uri_key`.
        If the URI is found, it creates a `CleanedURIRef` object; otherwise, it
        creates a blank node (`BNode`). Depending on whether `role_value` or
        `role_key` is provided, it either adds a specific role or a role from the
        dataset dictionary.

        Args:
            dataset_dict (dict): The dataset dictionary containing metadata.
            uri_key (str): The key to retrieve the URI from the dataset dictionary.
            role_value (str, optional): The specific role URI to be added. Defaults to None.
            role_key (str, optional): The key to retrieve the role from the dataset dictionary. Defaults to None.

        Returns:
            None
        """
        uri = self._get_dataset_value(dataset_dict, uri_key)
        if uri:
            details = CleanedURIRef(uri)
        else:
            details = BNode()
        
        if role_value:
            # Remove existing role if any
            existing_roles = list(self.g.objects(details, VCARD.role))
            for role in existing_roles:
                self.g.remove((details, VCARD.role, role))
            
            # Add new role
            self.g.add((details, VCARD.role, URIRef(role_value)))
        elif role_key:
            # Add role from dataset_dict
            self._add_triple_from_dict(
                dataset_dict, details,
                VCARD.role, role_key,
                _type=URIRef)
