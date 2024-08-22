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
from ckanext.schemingdcat.profiles.dcat_ap.eu_dcat_ap import EuDCATAPProfile
from ckanext.schemingdcat.profiles.dcat_config import (
    # Vocabs
    RDF,
    XSD,
    SCHEMA,
    RDFS,
    DCAT,
    DCATAP,
    DCT,
    CNT,
    ELI,
    # Default values
    metadata_field_names,
    default_translated_fields,
    es_dcat_default_values, 
    default_translated_fields_es_dcat,
    )


#TODO: Implement Spanish DCAT (NTI-RISP) profile
class EsNTIRISPProfile(EuDCATAPProfile):
    """
    A custom RDF profile based on the NTI-RISP for data portals in Spain

    Default values for some fields:
    
    ckanext-dcat/ckanext/dcat/.profiles.default_config.py

    More information and specification:

    https://datos.gob.es/es/documentacion/normativa-de-ambito-nacional
    https://datos.gob.es/es/documentacion/guia-de-aplicacion-de-la-norma-tecnica-de-interoperabilidad-de-reutilizacion-de

    """