import json
import re
import logging
from decimal import Decimal, DecimalException

from rdflib import term, URIRef, BNode, Literal
import ckantoolkit as toolkit

from ckan.lib.munge import munge_tag

from ckanext.dcat.utils import (
    resource_uri,
    DCAT_EXPOSE_SUBCATALOGS,
    DCAT_CLEAN_TAGS,
    publisher_uri_organization_fallback,
)

from ckanext.dcat.profiles.base import URIRefOrLiteral, CleanedURIRef

from ckanext.schemingdcat.profiles.base import (
    SchemingDCATRDFProfile,
    # Codelists
    MD_INSPIRE_REGISTER,
    MD_FORMAT,
    MD_EU_LANGUAGES,
    # Namespaces
    namespaces
)
from ckanext.schemingdcat.profiles.dcat_config import (
    # Vocabs
    RDF,
    XSD,
    SKOS,
    SCHEMA,
    RDFS,
    DCAT,
    DCATAP,
    DCT,
    ADMS,
    VCARD,
    FOAF,
    LOCN,
    GSP,
    OWL,
    SPDX,
    GEOJSON_IMT,
    CNT,
    ELI,
    EUROVOC,
    # Default values
    metadata_field_names,
    default_translated_fields,
    eu_dcat_ap_default_values,
    dcat_ap_default_licenses,
    )


config = toolkit.config

DISTRIBUTION_LICENSE_FALLBACK_CONFIG = "ckanext.dcat.resource.inherit.license"

log = logging.getLogger(__name__)

class BaseEuDCATAPProfile(SchemingDCATRDFProfile):
    """
    A base profile with common RDF properties across the different DCAT-AP versions

    """

    # Cache for mappings of licenses URL/title to ID built when needed in
    # _license().
    _translated_field_names = None

    def _parse_dataset_base(self, dataset_dict, dataset_ref):

        dataset_dict["extras"] = []
        dataset_dict["resources"] = []

        # Translated fields
        for key, field in default_translated_fields.items():
            predicate = field['rdf_predicate']
            value = self._object_value(dataset_ref, predicate, True)
            if value:
                dataset_dict[field['field_name']] = value

        # Basic fields
        for key, predicate in (
            ("title", DCT.title),
            ("notes", DCT.description),
            ("url", DCAT.landingPage),
            ("version", OWL.versionInfo),
            ('encoding', CNT.characterEncoding),
        ):
            value = self._object_value(dataset_ref, predicate)
            if value:
                dataset_dict[key] = value

        if not dataset_dict.get("version"):
            # adms:version was supported on the first version of the DCAT-AP
            value = self._object_value(dataset_ref, ADMS.version)
            if value:
                dataset_dict["version"] = value

        # Tags
        # replace munge_tag to noop if there's no need to clean tags
        do_clean = toolkit.asbool(config.get(DCAT_CLEAN_TAGS, False))
        tags_val = [
            munge_tag(tag) if do_clean else tag for tag in self._keywords(dataset_ref)
        ]
        tags = [{"name": tag} for tag in tags_val]
        dataset_dict["tags"] = tags

        # Extras

        #  Simple values
        for key, predicate in (
            ("issued", DCT.issued),
            ("modified", DCT.modified),
            ("identifier", DCT.identifier),
            ("version_notes", ADMS.versionNotes),
            ("frequency", DCT.accrualPeriodicity),
            ("provenance", DCT.provenance),
            ("dcat_type", DCT.type),
        ):
            value = self._object_value(dataset_ref, predicate)
            if value:
                dataset_dict["extras"].append({"key": key, "value": value})

        #  Lists
        for key, predicate, in (
            ("language", DCT.language),
            ("theme", DCAT.theme),
            ("alternate_identifier", ADMS.identifier),
            ("conforms_to", DCT.conformsTo),
            ("documentation", FOAF.page),
            ("related_resource", DCT.relation),
            ("has_version", DCT.hasVersion),
            ("is_version_of", DCT.isVersionOf),
            ("source", DCT.source),
            ("sample", ADMS.sample),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict["extras"].append({"key": key, "value": json.dumps(values)})

        # Contact details
        contact = self._contact_details(dataset_ref, DCAT.contactPoint)
        if not contact:
            # adms:contactPoint was supported on the first version of DCAT-AP
            contact = self._contact_details(dataset_ref, ADMS.contactPoint)

        if contact:
            for key in ("uri", "name", "email", "url", "role"):
                if contact.get(key):
                    dataset_dict["extras"].append(
                        {"key": "contact_{0}".format(key), "value": contact.get(key)}
                    )

        # Publisher
        publisher = self._publisher(dataset_ref, DCT.publisher)
        for key in ("uri", "name", "email", "url", "type", "identifier", "role"):
            if publisher.get(key):
                dataset_dict["extras"].append(
                    {"key": "publisher_{0}".format(key), "value": publisher.get(key)}
                )
                
        # Author
        author = self._author(dataset_ref, DCT.creator)
        for key in ("uri", "name", "email", "url", "role"):
            if author.get(key):
                dataset_dict["extras"].append(
                    {"key": "author_{0}".format(key), "value": author.get(key)}
                )

        # Temporal
        start, end = self._time_interval(dataset_ref, DCT.temporal)
        if start:
            dataset_dict["extras"].append({"key": "temporal_start", "value": start})
        if end:
            dataset_dict["extras"].append({"key": "temporal_end", "value": end})

        # Spatial
        spatial = self._spatial(dataset_ref, DCT.spatial)
        for key in ("uri", "text", "geom"):
            self._add_spatial_to_dict(dataset_dict, key, spatial)

        # Dataset URI (explicitly show the missing ones)
        dataset_uri = str(dataset_ref) if isinstance(dataset_ref, term.URIRef) else ""
        dataset_dict["extras"].append({"key": "uri", "value": dataset_uri})

        # access_rights
        access_rights = self._access_rights(dataset_ref, DCT.accessRights)
        if access_rights:
            dataset_dict["extras"].append(
                {"key": "access_rights", "value": access_rights}
            )

        # License
        if "license_id" not in dataset_dict:
            dataset_dict["license_id"] = self._license(dataset_ref)

        # Source Catalog
        if toolkit.asbool(config.get(DCAT_EXPOSE_SUBCATALOGS, False)):
            catalog_src = self._get_source_catalog(dataset_ref)
            if catalog_src is not None:
                src_data = self._extract_catalog_dict(catalog_src)
                dataset_dict["extras"].extend(src_data)

        # Resources
        for distribution in self._distributions(dataset_ref):

            resource_dict = {}

            #  Simple values
            for key, predicate in (
                ("name", DCT.title),
                ("description", DCT.description),
                ("access_url", DCAT.accessURL),
                ("download_url", DCAT.downloadURL),
                ("issued", DCT.issued),
                ("modified", DCT.modified),
                ("status", ADMS.status),
                ("license", DCT.license),
            ):
                value = self._object_value(distribution, predicate)
                if value:
                    resource_dict[key] = value

            resource_dict["url"] = self._object_value(
                distribution, DCAT.downloadURL
            ) or self._object_value(distribution, DCAT.accessURL)
            #  Lists
            for key, predicate in (
                ("language", DCT.language),
                ("documentation", FOAF.page),
                ("conforms_to", DCT.conformsTo),
                ("metadata_profile", DCT.conformsTo),
            ):
                values = self._object_value_list(distribution, predicate)
                if values:
                    resource_dict[key] = json.dumps(values)

            # rights
            rights = self._access_rights(distribution, DCT.rights)
            if rights:
                resource_dict["rights"] = rights

            # Format and media type
            normalize_ckan_format = toolkit.asbool(
                config.get("ckanext.dcat.normalize_ckan_format", True)
            )
            imt, label = self._distribution_format(distribution, normalize_ckan_format)

            if imt:
                resource_dict["mimetype"] = imt

            if label:
                resource_dict["format"] = label
            elif imt:
                resource_dict["format"] = imt

            # Size
            size = self._object_value_int(distribution, DCAT.byteSize)
            if size is not None:
                resource_dict["size"] = size

            # Checksum
            for checksum in self.g.objects(distribution, SPDX.checksum):
                algorithm = self._object_value(checksum, SPDX.algorithm)
                checksum_value = self._object_value(checksum, SPDX.checksumValue)
                if algorithm:
                    resource_dict["hash_algorithm"] = algorithm
                if checksum_value:
                    resource_dict["hash"] = checksum_value

            # Distribution URI (explicitly show the missing ones)
            resource_dict["uri"] = (
                str(distribution) if isinstance(distribution, term.URIRef) else ""
            )

            # Remember the (internal) distribution reference for referencing in
            # further profiles, e.g. for adding more properties
            resource_dict["distribution_ref"] = str(distribution)

            dataset_dict["resources"].append(resource_dict)

        if self.compatibility_mode:
            # Tweak the resulting dict to make it compatible with previous
            # versions of the ckanext-dcat parsers
            for extra in dataset_dict["extras"]:
                if extra["key"] in (
                    "issued",
                    "modified",
                    "publisher_name",
                    "publisher_email",
                ):

                    extra["key"] = "dcat_" + extra["key"]

                if extra["key"] == "language":
                    extra["value"] = ",".join(sorted(json.loads(extra["value"])))

        return dataset_dict

    def _graph_from_dataset_base(self, dataset_dict, dataset_ref):

        g = self.g

        for prefix, namespace in namespaces.items():
            g.bind(prefix, namespace)

        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        # Translated fields
        translated_items = [
            (
                default_translated_fields[key]['field_name'],
                default_translated_fields[key]['rdf_predicate'],
                default_translated_fields[key]['fallbacks'],
                default_translated_fields[key]['_type'],
                default_translated_fields[key]['_class'],
                default_translated_fields[key]['required_lang']
            )
            for key in default_translated_fields
        ]
        
        self._add_triples_from_dict(
            _dict=dataset_dict,
            subject=dataset_ref,
            items=translated_items,
            list_value=False,
            date_value=False,
            multilang=True
        )
                
        # Create a set of the translated field names
        self._translated_field_names = {item[0] for item in translated_items}
        
        # Basic fields without translating fields
        basic_items = [
            ("title", DCT.title, None, Literal),
            ("notes", DCT.description, None, Literal),
            ("url", DCAT.landingPage, None, URIRef, FOAF.Document),
            ("identifier", DCT.identifier, ["guid", "id"], URIRefOrLiteral),
            ("version", OWL.versionInfo, ["dcat_version"], Literal),
            ("version_notes", ADMS.versionNotes, None, Literal),
            ("frequency", DCT.accrualPeriodicity, None, URIRefOrLiteral, DCT.Frequency),
            ("access_rights", DCT.accessRights, None, URIRefOrLiteral, DCT.AccessRights),
            ("dcat_type", DCT.type, None, URIRefOrLiteral),
            ("provenance", DCT.provenance, None, URIRefOrLiteral, DCT.ProvenanceStatement),
        ]
        
        # Filter basic fields to exclude those already in the translated fields
        filtered_basic_items = [item for item in basic_items if item[0] not in self._translated_field_names]
        
        self._add_triples_from_dict(dataset_dict, dataset_ref, filtered_basic_items)

        # Access Rights
        # DCAT-AP: http://publications.europa.eu/en/web/eu-vocabularies/at-dataset/-/resource/dataset/access-right
        access_rights_value = self._get_dataset_value(dataset_dict, "access_rights")
        
        if access_rights_value:
            if "authority/access-right" in access_rights_value:
                g.add((dataset_ref, DCT.accessRights, URIRef(access_rights_value)))
            else:
                g.remove((dataset_ref, DCT.accessRights, URIRef(access_rights_value)))
                g.add((dataset_ref, DCT.accessRights, URIRef(eu_dcat_ap_default_values["access_rights"])))
        else:
            g.add((dataset_ref, DCT.accessRights, URIRef(eu_dcat_ap_default_values["access_rights"])))
            
        # Tags
        # Pre-process keywords inside INSPIRE MD Codelists and update dataset_dict
        dataset_tag_base = f'{dataset_ref.split("/dataset/")[0]}'
        tag_names = [tag["name"].replace(" ", "").lower() for tag in dataset_dict.get("tags", [])]

        # Search for matching keywords in MD_INSPIRE_REGISTER and update dataset_dict
        if tag_names:             
            self._search_values_codelist_add_to_graph(MD_INSPIRE_REGISTER, tag_names, dataset_dict, dataset_ref, dataset_tag_base, g, DCAT.keyword)

        # Dates
        items = [
            ("issued", DCT.issued, ["metadata_created"], Literal),
            ("modified", DCT.modified, ["metadata_modified"], Literal),
        ]
        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

        #  Lists
        items = [
            ("language", DCT.language, None, URIRefOrLiteral, DCT.LinguisticSystem),
            ("theme", DCAT.theme, None, URIRef),
            ("conforms_to", DCT.conformsTo, None, URIRefOrLiteral, DCT.Standard),
            ("alternate_identifier", ADMS.identifier, None, URIRefOrLiteral, ADMS.Identifier),
            ("documentation", FOAF.page, None, URIRefOrLiteral, FOAF.Document),
            ("related_resource", DCT.relation, None, URIRefOrLiteral, RDFS.Resource),
            ("has_version", DCT.hasVersion, None, URIRefOrLiteral),
            ("is_version_of", DCT.isVersionOf, None, URIRefOrLiteral),
            ("source", DCT.source, None, URIRefOrLiteral),
            ("sample", ADMS.sample, None, URIRefOrLiteral, DCAT.Distribution),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        # DCAT Themes (https://publications.europa.eu/resource/authority/data-theme)
        # Append the final result to the graph
        dcat_themes = self._themes(dataset_ref)
        for theme in dcat_themes:
            g.add((dataset_ref, DCAT.theme, URIRefOrLiteral(theme)))

        # Contact details
        if any([
            self._get_dataset_value(dataset_dict, "contact_uri"),
            self._get_dataset_value(dataset_dict, "contact_name"),
            self._get_dataset_value(dataset_dict, "contact_email"),
            self._get_dataset_value(dataset_dict, "contact_url"),
        ]):

            contact_uri = self._get_dataset_value(dataset_dict, "contact_uri")
            if contact_uri:
                contact_details = CleanedURIRef(contact_uri)
            else:
                contact_details = BNode()

            g.add((contact_details, RDF.type, VCARD.Kind))
            g.add((dataset_ref, DCAT.contactPoint, contact_details))

            # Add name
            self._add_triple_from_dict(
                dataset_dict, contact_details,
                VCARD.fn, "contact_name"
            )
            # Add mail address as URIRef, and ensure it has a mailto: prefix
            self._add_triple_from_dict(
                dataset_dict, contact_details,
                VCARD.hasEmail,
                "contact_email",
                _type=URIRef,
                value_modifier=self._add_mailto,
            )
            # Add contact URL
            self._add_triple_from_dict(
                dataset_dict, contact_details,
                VCARD.hasURL, "contact_url",
                _type=URIRef)

            # Add contact role
            g.add((contact_details, VCARD.role, URIRef(eu_dcat_ap_default_values["contact_role"])))

        # Resource maintainer/contact 
        if any([
            self._get_dataset_value(dataset_dict, "maintainer"),
            self._get_dataset_value(dataset_dict, "maintainer_uri"),
            self._get_dataset_value(dataset_dict, "maintainer_email"),
            self._get_dataset_value(dataset_dict, "maintainer_url"),
        ]):
            maintainer_uri = self._get_dataset_value(dataset_dict, "maintainer_uri")
            if maintainer_uri:
                maintainer_details = CleanedURIRef(maintainer_uri)
            else:
                maintainer_details = dataset_ref + "/maintainer"
                
            g.add((maintainer_details, RDF.type, VCARD.Kind))
            g.add((dataset_ref, DCAT.contactPoint, maintainer_details))

            ## Add name & mail
            self._add_triple_from_dict(
                dataset_dict, maintainer_details,
                VCARD.fn, "maintainer"
            )
            # Add mail address as URIRef, and ensure it has a mailto: prefix
            self._add_triple_from_dict(
                dataset_dict, maintainer_details,
                VCARD.hasEmail,
                "maintainer_email",
                _type=URIRef,
                value_modifier=self._add_mailto,
            )
            # Add maintainer URL
            self._add_triple_from_dict(
                dataset_dict, maintainer_details,
                VCARD.hasURL, "maintainer_url",
                _type=URIRef)

            # Add maintainer role
            g.add((maintainer_details, VCARD.role, URIRef(eu_dcat_ap_default_values["maintainer_role"])))

        # Resource author
        if any([
            self._get_dataset_value(dataset_dict, "author"),
            self._get_dataset_value(dataset_dict, "author_uri"),
            self._get_dataset_value(dataset_dict, "author_email"),
            self._get_dataset_value(dataset_dict, "author_url"),
        ]):
            author_uri = self._get_dataset_value(dataset_dict, "author_uri")
            if author_uri:
                author_details = CleanedURIRef(author_uri)
            else:
                author_details = dataset_ref + "/author"
                
            g.add((author_details, RDF.type, VCARD.Organization))
            g.add((dataset_ref, DCT.creator, author_details))

            ## Add name & mail
            self._add_triple_from_dict(
                dataset_dict, author_details,
                VCARD.fn, "author"
            )
            # Add mail address as URIRef, and ensure it has a mailto: prefix
            self._add_triple_from_dict(
                dataset_dict, author_details,
                VCARD.hasEmail,
                "author_email",
                _type=URIRef,
                value_modifier=self._add_mailto,
            )
            # Add author URL
            self._add_triple_from_dict(
                dataset_dict, author_details,
                VCARD.hasURL, "author_url",
                _type=URIRef)

            # Add author role
            g.add((author_details, VCARD.role, URIRef(eu_dcat_ap_default_values["author_role"])))

        # Provenance: dataset dct:provenance dct:ProvenanceStatement
        provenance_details = dataset_ref + "/provenance"
        provenance_statement = self._get_dataset_value(dataset_dict, "provenance")
        if provenance_statement:
            g.add((dataset_ref, DCT.provenance, provenance_details))
            g.add((provenance_details, RDF.type, DCT.ProvenanceStatement))
            
            if isinstance(provenance_statement, dict):
                self._add_multilang_triple(provenance_details, RDFS.label, provenance_statement)
            else:
                g.add((provenance_details, RDFS.label, Literal(provenance_statement)))

        # Publisher
        publisher_ref = None

        if dataset_dict.get("publisher"):
            # Scheming publisher field: will be handled in a separate profile
            pass
        elif any(
            [
                self._get_dataset_value(dataset_dict, "publisher_uri"),
                self._get_dataset_value(dataset_dict, "publisher_name"),
            ]
        ):
            # Legacy publisher_* extras
            publisher_uri = self._get_dataset_value(dataset_dict, "publisher_uri")
            publisher_name = self._get_dataset_value(dataset_dict, "publisher_name")
            if publisher_uri:
                publisher_ref = CleanedURIRef(publisher_uri)
            else:
                # No publisher_uri
                publisher_ref = BNode()
            publisher_details = {
                "name": publisher_name,
                "email": self._get_dataset_value(dataset_dict, "publisher_email"),
                "url": self._get_dataset_value(dataset_dict, "publisher_url"),
                "type": self._get_dataset_value(dataset_dict, "publisher_type"),
                "identifier": self._get_dataset_value(dataset_dict, "publisher_identifier"),
                "uri": publisher_uri,
            }
        elif dataset_dict.get("organization"):
            # Fall back to dataset org
            org_id = dataset_dict["organization"]["id"]
            org_dict = None
            if org_id in self._org_cache:
                org_dict = self._org_cache[org_id]
            else:
                try:
                    org_dict = toolkit.get_action("organization_show")(
                        {"ignore_auth": True}, {"id": org_id}
                    )
                    self._org_cache[org_id] = org_dict
                except toolkit.ObjectNotFound:
                    pass
            if org_dict:
                publisher_ref = CleanedURIRef(
                    publisher_uri_organization_fallback(dataset_dict)
                )
                publisher_details = {
                    "name": org_dict.get("title"),
                    "email": org_dict.get("publisher_email") or org_dict.get("email"),
                    "url": org_dict.get("url"),
                    "type": org_dict.get("publisher_type") or org_dict.get("dcat_type"),
                    "identifier": org_dict.get("identifier"),
                }
        #FIXME: Review bugs when serialize. Add to graph
        if publisher_ref:
            g.add((publisher_ref, RDF.type, FOAF.Agent))
            g.add((dataset_ref, DCT.publisher, publisher_ref))
            items = [
                ("name", FOAF.name, None, Literal),
                ("email", FOAF.mbox, None, Literal),
                ("url", FOAF.homepage, None, URIRef),
                ("type", DCT.type, None, URIRefOrLiteral),
            ]

            # Add publisher role
            g.add((publisher_details, VCARD.role, URIRef(eu_dcat_ap_default_values["publisher_role"])))

            self._add_triples_from_dict(publisher_details, publisher_ref, items)

        # TODO: Deprecated: https://semiceu.github.io/GeoDCAT-AP/drafts/latest/#deprecated-properties-for-period-of-time
        # Temporal
        start = self._get_dataset_value(dataset_dict, "temporal_start")
        end = self._get_dataset_value(dataset_dict, "temporal_end")
        if start or end:
            temporal_extent = BNode()

            g.add((temporal_extent, RDF.type, DCT.PeriodOfTime))
            if start:
                self._add_date_triple(temporal_extent, SCHEMA.startDate, start)
            if end:
                self._add_date_triple(temporal_extent, SCHEMA.endDate, end)
            g.add((dataset_ref, DCT.temporal, temporal_extent))

        # Spatial
        spatial_text = self._get_dataset_value(dataset_dict, "spatial_text")
        spatial_geom = self._get_dataset_value(dataset_dict, "spatial")

        if spatial_text or spatial_geom:
            spatial_ref = self._get_or_create_spatial_ref(dataset_dict, dataset_ref)

            if spatial_text:
                g.add((spatial_ref, SKOS.prefLabel, Literal(spatial_text)))

            if spatial_geom:
                self._add_spatial_value_to_graph(
                    spatial_ref, LOCN.geometry, spatial_geom
                )

        # Coordinate Reference System
        if self._get_dataset_value(dataset_dict, "reference_system"):
            crs_uri = self._get_dataset_value(dataset_dict, "reference_system")
            crs_details = CleanedURIRef(crs_uri)
            g.add((crs_details, RDF.type, DCT.Standard))
            g.add((crs_details, DCT.type, CleanedURIRef(eu_dcat_ap_default_values["reference_system_type"])))
            g.add((dataset_ref, DCT.conformsTo, crs_details))

        # Update licenses if it is in dcat_ap_default_licenses. DCAT-AP Compliance
        if "license_url" in dataset_dict:
            license_info = dcat_ap_default_licenses.get(dataset_dict["license_url"], None)
            if license_info:
                dataset_dict["license_id"] = license_info["fallback_license_id"]
                dataset_dict["license_url"] = license_info["fallback_license_url"]

        # Use fallback license if set in config
        resource_license_fallback = None
        if toolkit.asbool(config.get(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, False)):
            if "license_id" in dataset_dict and isinstance(
                URIRefOrLiteral(dataset_dict["license_id"]), URIRef
            ):
                resource_license_fallback = dataset_dict["license_id"]
            elif "license_url" in dataset_dict and isinstance(
                URIRefOrLiteral(dataset_dict["license_url"]), URIRef
            ):
                resource_license_fallback = dataset_dict["license_url"]

        # Resources
        for resource_dict in dataset_dict.get("resources", []):

            distribution = CleanedURIRef(resource_uri(resource_dict))

            g.add((dataset_ref, DCAT.distribution, distribution))

            g.add((distribution, RDF.type, DCAT.Distribution))

            #  Simple values
            items = [
                ("name", DCT.title, None, Literal),
                ("description", DCT.description, None, Literal),
                ("status", ADMS.status, None, URIRefOrLiteral),
                ("rights", DCT.rights, None, URIRefOrLiteral, DCT.RightsStatement),
                ("license", DCT.license, None, URIRefOrLiteral, DCT.LicenseDocument),
                ("access_url", DCAT.accessURL, None, URIRef, RDFS.Resource),
                ("download_url", DCAT.downloadURL, None, URIRef, RDFS.Resource),
                ("encoding", CNT.characterEncoding, None, Literal),
            ]

            self._add_triples_from_dict(resource_dict, distribution, items)

            #  Lists
            items = [
                ("documentation", FOAF.page, None, URIRefOrLiteral, FOAF.Document),
                ("language", DCT.language, None, URIRefOrLiteral, DCT.LinguisticSystem),
                ("conforms_to", DCT.conformsTo, None, URIRefOrLiteral, DCT.Standard),
                ("metadata_profile", DCT.conformsTo, None, URIRef),
            ]
            self._add_list_triples_from_dict(resource_dict, distribution, items)

            # Set default license for distribution if needed and available

            if resource_license_fallback and not (distribution, DCT.license, None) in g:
                g.add(
                    (
                        distribution,
                        DCT.license,
                        URIRefOrLiteral(resource_license_fallback),
                    )
                )
            # TODO: add an actual field to manage this
            if (distribution, DCT.license, None) in g:
                g.add(
                    (
                        list(g.objects(distribution, DCT.license))[0],
                        DCT.type,
                        URIRef("http://purl.org/adms/licencetype/UnknownIPR")
                    )
                )

            # Format
            mimetype = resource_dict.get("mimetype")
            fmt = resource_dict.get("format")

            # IANA media types (either URI or Literal) should be mapped as mediaType.
            # In case format is available and mimetype is not set or identical to format,
            # check which type is appropriate.
            if fmt and (not mimetype or mimetype == fmt):
                if (
                    "iana.org/assignments/media-types" in fmt
                    or not fmt.startswith("http")
                    and "/" in fmt
                ):
                    # output format value as dcat:mediaType instead of dct:format
                    mimetype = fmt
                    fmt = None
                else:
                    # Use dct:format
                    mimetype = None

            if mimetype:
                mimetype = URIRefOrLiteral(mimetype)
                g.add((distribution, DCAT.mediaType, mimetype))
                if isinstance(mimetype, URIRef):
                    g.add((mimetype, RDF.type, DCT.MediaType))
            elif fmt:
                mime_val = self._search_value_codelist(MD_FORMAT, fmt, "id", "media_type") or None
                if mime_val and mime_val != fmt:
                    g.add((distribution, DCAT.mediaType, URIRefOrLiteral(mime_val)))

            # Try to match format field
            fmt = self._search_value_codelist(MD_FORMAT, fmt, "label", "id") or fmt

            # Add format to graph
            if fmt:
                fmt = URIRefOrLiteral(fmt)
                g.add((distribution, DCT["format"], fmt))
                if isinstance(fmt, URIRef):
                    g.add((fmt, RDF.type, DCT.MediaTypeOrExtent))

            # URL fallback and old behavior
            url = resource_dict.get("url")
            download_url = resource_dict.get("download_url")
            access_url = resource_dict.get("access_url")
            # Use url as fallback for access_url if access_url is not set and download_url is not equal
            if url and not access_url:
                if (not download_url) or (download_url and url != download_url):
                    self._add_triple_from_dict(
                        resource_dict, distribution, DCAT.accessURL, "url", _type=URIRef
                    )

            # Dates
            items = [
                ("issued", DCT.issued, ["created"], Literal),
                ("modified", DCT.modified, ["metadata_modified"], Literal),
            ]

            self._add_date_triples_from_dict(resource_dict, distribution, items)

            # Access Rights
            # DCAT-AP: http://publications.europa.eu/en/web/eu-vocabularies/at-dataset/-/resource/dataset/access-right
            rights_value = self._get_resource_value(resource_dict, 'rights')
            if rights_value and 'authority/access-right' in rights_value:
                rights_uri = URIRef(rights_value)
            else:
                rights_uri = URIRef(eu_dcat_ap_default_values['access_rights'])
            
            if rights_value:
                g.remove((distribution, DCT.rights, URIRef(rights_value)))
            g.add((distribution, DCT.rights, rights_uri))
            
            # Numbers
            if resource_dict.get("size"):
                try:
                    g.add(
                        (
                            distribution,
                            DCAT.byteSize,
                            Literal(Decimal(resource_dict["size"]), datatype=XSD.decimal),
                        )
                    )
                except (ValueError, TypeError, DecimalException):
                    g.add((distribution, DCAT.byteSize, Literal(resource_dict["size"])))
            # Checksum
            if resource_dict.get("hash"):
                checksum = BNode()
                g.add((checksum, RDF.type, SPDX.Checksum))
                g.add(
                    (
                        checksum,
                        SPDX.checksumValue,
                        Literal(resource_dict["hash"], datatype=XSD.hexBinary),
                    )
                )

                if resource_dict.get("hash_algorithm"):
                    checksum_algo = URIRefOrLiteral(resource_dict["hash_algorithm"])
                    g.add(
                        (
                            checksum,
                            SPDX.algorithm,
                            checksum_algo,
                        )
                    )
                    if isinstance(checksum_algo, URIRef):
                        g.add((checksum_algo, RDF.type, SPDX.ChecksumAlgorithm))

                g.add((distribution, SPDX.checksum, checksum))

    def _graph_from_catalog_base(self, catalog_dict, catalog_ref):

        g = self.g

        for prefix, namespace in namespaces.items():
            g.bind(prefix, namespace)

        g.add((catalog_ref, RDF.type, DCAT.Catalog))

        # Basic fields
        license, publisher_identifier, access_rights, spatial_uri, language = [
            self._get_catalog_field(field_name='license_url'),
            self._get_catalog_field(field_name='publisher_identifier', fallback='publisher_uri'),
            self._get_catalog_field(field_name='access_rights'),
            self._get_catalog_field(field_name='spatial_uri'),
            self._search_value_codelist(MD_EU_LANGUAGES, config.get('ckan.locale_default'), "label","id") or eu_dcat_ap_default_values['language'],
            ]

        # Mandatory elements by NTI-RISP (datos.gob.es)
        items = [
            ("identifier", DCT.identifier, f'{config.get("ckan_url")}/catalog.rdf', Literal),
            ("title", DCT.title, config.get("ckan.site_title"), Literal),
            ("encoding", CNT.characterEncoding, "UTF-8", Literal),
            ("description", DCT.description, config.get("ckan.site_description"), Literal),
            ("publisher_identifier", DCT.publisher, publisher_identifier, URIRef),
            ("language", DCT.language, language, URIRefOrLiteral),
            ("spatial_uri", DCT.spatial, spatial_uri, URIRefOrLiteral),
            ("theme_taxonomy", DCAT.themeTaxonomy, eu_dcat_ap_default_values["theme_taxonomy"], URIRef),
            ("homepage", FOAF.homepage, config.get("ckan_url"), URIRef),
            ("license", DCT.license, license, URIRef),
            ("conforms_to", DCT.conformsTo, eu_dcat_ap_default_values["conformance"], URIRef),
            ("access_rights", DCT.accessRights, access_rights, URIRefOrLiteral),
        ]
                 
        for item in items:
            key, predicate, fallback, _type = item
            if catalog_dict:
                value = catalog_dict.get(key, fallback)
            else:
                value = fallback
            if value:
                g.add((catalog_ref, predicate, _type(value)))

        # Dates
        modified = self._last_catalog_modification()
        if modified:
            self._add_date_triple(catalog_ref, DCT.modified, modified)
