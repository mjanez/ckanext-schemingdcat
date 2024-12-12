import logging
import urllib3

from owslib.csw import CatalogueServiceWeb as OwsCatalogueServiceWeb
from owslib.util import Authentication
from owslib.fes import PropertyIsLike, PropertyIsEqualTo, SortBy, SortProperty
from urllib.parse import urlparse, urlunparse, urlencode

from ckanext.schemingdcat.config import (
    CSW_DEFAULT_LIMIT,
    CQL_QUERY_DEFAULT,
    CQL_SEARCH_TERM_DEFAULT,
    OUTPUT_SCHEMA
)

log = logging.getLogger(__name__)


# Disable SSL warnings.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Custom exceptions.
class CSWNotFoundError(Exception):
    pass

class InvalidCSWServiceError(Exception):
    """Exception raised when the CSW service URL is invalid or unavailable."""
    pass

class SchemingDCATCatalogueServiceWeb(object):
    """
    A class to interact with a CSW (Catalogue Service for the Web) server.

    This class provides methods to retrieve records from a CSW server using various query parameters.

    Attributes:
        csw_url (str): The URL of the CSW server.
        csw (OwsCatalogueServiceWeb): An instance of the OWSLib CatalogueServiceWeb class.
        schema (str): The output schema for the CSW records.

    Args:
        url (str): The URL of the CSW server.
        ssl_verify (bool): Whether to verify the SSL certificate. Default is True.
    """

    def __init__(self, url, ssl_verify=True):
        """
        Initializes the SchemingDCATCatalogueServiceWeb with the given URL and SSL verification setting.

        Args:
            url (str): The URL of the CSW server.
            ssl_verify (bool): Whether to verify the SSL certificate. Default is True.
        """
        self.csw_url = self.get_csw_url(url)
        # Create an instance of Authentication with SSL_VERIFY
        auth = Authentication(verify=ssl_verify)
        # Pass 'auth' when initializing CatalogueServiceWeb
        self.csw = OwsCatalogueServiceWeb(self.csw_url, auth=auth)
        self.schema = OUTPUT_SCHEMA

    def get_csw_url(self, url):
        """
        Constructs the CSW URL with the required service parameter.

        Args:
            url (str): The base URL of the CSW server.

        Returns:
            str: The constructed CSW URL.
        """
        parsed_url = urlparse(url)
        query = urlencode({"service": "CSW"})
        csw_url = urlunparse((
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, query, parsed_url.fragment
        ))
        return csw_url

    def get_csw_records(self, cql=None, cql_query=None,
                        cql_search_term=None, cql_use_like=False,typenames="csw:Record",
                        limit=CSW_DEFAULT_LIMIT, esn="full", outputschema=OUTPUT_SCHEMA,
                        maxrecords=75, startposition=0, sortproperty='dc:identifier'):
        """
        Retrieve records from a CSW server.

        Args:
            typenames (str, optional): The typeNames to query against. Defaults to "csw:Record".
            limit (int, optional): The maximum number of records to return. No records are returned if 0. Defaults to None.
            esn (str, optional): The ElementSetName 'full', 'brief' or 'summary'. Defaults to 'summary'.
            outputschema (str, optional): The outputSchema. Defaults to 'http://www.opengis.net/cat/csw/2.0.2'.
            page (int, optional): The number of records to return per page. Defaults to 30.
            startposition (int, optional): Requests a slice of the result set, starting at this position. Defaults to 0.
            sortproperty (str, optional): The sortProperty. Defaults to 'dc:identifier'.

        Returns:
            record_ids (list): A list of record identifiers from the CSW server.

        Additional Information:
            getrecords2 (OWSLib): Construct and process a GetRecords request in order to retrieve metadata records from a CSW.
            Parameters
            ----------
            - constraints: the list of constraints (OgcExpression from owslib.fes module)
            - sortby: an OGC SortBy object (SortBy from owslib.fes module)
            - typenames: the typeNames to query against (default is csw:Record)
            - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'summary')
            - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
            - format: the outputFormat (default is 'application/xml')
            - startposition: requests a slice of the result set, starting at this position (default is 0)
            - maxrecords: the maximum number of records to return. No records are returned if 0 (default is 10)
            - cql: common query language text.  Note this overrides bbox, qtype, keywords
            - xml: raw XML request.  Note this overrides all other options
            - resulttype: the resultType 'hits', 'results', 'validate' (default is 'results')
            - distributedsearch: `bool` of whether to trigger distributed search
            - hopcount: number of message hops before search is terminated (default is 1)
        """
        self.csw.sortby = SortBy([SortProperty(sortproperty)])
        record_ids = []

        # Configure parameters for the query
        csw_args = {
            "typenames": typenames,
            "esn": esn,
            "maxrecords": maxrecords,
            "outputschema": outputschema,
            "sortby": self.csw.sortby,
            "startposition": startposition
        }

        log.info("Making CSW request: 'getrecords2()': %s", csw_args)

        if cql_query and cql_search_term:
            log.debug('cql_query: %s', cql_query)
            log.debug('cql_search_term: %s', cql_search_term)
            if cql_use_like or cql_query == CQL_QUERY_DEFAULT:
                log.debug('CQL_QUERY_DEFAULT: %s', CQL_QUERY_DEFAULT)
                csw_args["constraints"] = [
                    PropertyIsLike(cql_query, cql_search_term)
                ]
            else:
                csw_args["constraints"] = [
                    PropertyIsEqualTo(cql_query, cql_search_term)
                ]
        elif cql:
            log.debug('cql: %s', cql)
            csw_args["cql"] = cql
        elif CQL_SEARCH_TERM_DEFAULT is not None:
            log.debug('CQL_SEARCH_TERM_DEFAULT: %s', CQL_SEARCH_TERM_DEFAULT)
            csw_args["constraints"] = [
                PropertyIsEqualTo(CQL_QUERY_DEFAULT, CQL_SEARCH_TERM_DEFAULT)
            ]

        log.debug('csw_args: %s', csw_args)
        nextrecord = startposition

        while nextrecord is not None:
            csw_args["startposition"] = nextrecord
            self.csw.getrecords2(**csw_args)
            if self.csw.response is None or self.csw.results['matches'] == 0:
               raise CSWNotFoundError(
                    "No dataset found for url {} with arguments {}"
                    .format(self.csw.url, csw_args))

            if limit and len(record_ids) >= limit:
                break

            if self.csw.results['returned'] > 0:
                if 0 < self.csw.results['nextrecord']\
                        <= self.csw.results['matches']:
                    nextrecord = self.csw.results['nextrecord']
                else:
                    nextrecord = None
                for id in self.csw.records.keys():
                    record_ids.append(id)

        log.debug('CSW records matching constraints: %s', len(record_ids))

        return record_ids

    def get_record_by_id(self, csw_id):
        self.csw.getrecordbyid(id=[csw_id], outputschema=self.schema)
        csw_record_as_string = self.csw.response
        if csw_record_as_string:
            return csw_record_as_string
        else:
            return None
