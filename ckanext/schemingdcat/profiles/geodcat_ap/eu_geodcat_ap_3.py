import json
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

from ckanext.schemingdcat.profiles.geodcat_ap.eu_geodcat_ap_2 import EuGeoDCATAP2Profile
from ckanext.schemingdcat.profiles.dcat_config import (
    # Vocabs
    ADMS,
    RDF,
    DCAT,
    DCATAP,
    GEODCATAP,
    VCARD,
    # Default values
    metadata_field_names,
    eu_geodcat_ap_default_values,
    )

#TODO: Implement GeoDCAT-AP 3 profile
class EuGeoDCATAP3Profile(EuGeoDCATAP2Profile):
    """
    A custom RDF profile based on the GeoDCAT-AP 3 for data portals in Europe

    More information and specification:

    https://joinup.ec.europa.eu/collection/semic-support-centre/solution/geodcat-application-profile-data-portals-europe

    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # call super method
        super(EuGeoDCATAP3Profile, self).parse_dataset(dataset_dict, dataset_ref)

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # call super method
        super(EuGeoDCATAP3Profile, self).graph_from_dataset(
            dataset_dict, dataset_ref
        )

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        # call super method
        super(EuGeoDCATAP3Profile, self).graph_from_catalog(
            catalog_dict, catalog_ref
        )