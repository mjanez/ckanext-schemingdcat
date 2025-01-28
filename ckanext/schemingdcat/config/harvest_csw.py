import os

# Define the base directory of the repository dynamically
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# XLSTransformer configuration
XLST_MAPPINGS_DIR = os.path.join(BASE_DIR, 'ckanext/schemingdcat/lib/csw_mapper/xslt/mappings')
# GeoDCAT-AP official XSLT
DEFAULT_XSLT_FILE = 'https://raw.githubusercontent.com/SEMICeu/iso-19139-to-dcat-ap/refs/heads/geodcat-ap-2.0.0/iso-19139-to-dcat-ap.xsl'

# CSW processor configuration
CSW_DEFAULT_LIMIT = None
CQL_QUERY_DEFAULT = 'csw:AnyText'
CQL_SEARCH_TERM_DEFAULT = None
OUTPUT_SCHEMA = 'http://www.isotc211.org/2005/gmd'

# Define normalized protocol constants
DOWNLOAD_PROTOCOL = "WWW:DOWNLOAD"
OGC_WMTS_PROTOCOL = "OGC:WMTS"
OGC_WFS_PROTOCOL = "OGC:WFS"
OGC_WMS_PROTOCOL = "OGC:WMS"
LINKED_DATA_PROTOCOL = "LINKED:DATA"
APP_PROTOCOL = "WWW:DOWNLOAD-APP"
ESRI_REST_PROTOCOL = "ESRI:REST"
MAP_PROTOCOL = 'MAP:PREVIEW'

# DCAT-AP HVD
INSPIRE_HVD_CATEGORY = "http://data.europa.eu/bna/c_ac64a52d"
INSPIRE_HVD_APPLICABLE_LEGISLATION = "http://data.europa.eu/eli/reg_impl/2023/138/oj"

# Define a comprehensive mapping of protocol identifiers to normalized protocols
PROTOCOL_MAPPING = {
    'esri:aims-http-configuration': 'HTTP',
    'esri:aims-http-get-feature': 'HTTP',  # arcims internet feature map service
    'esri:aims-http-get-image': 'HTTP',    # arcims internet image map service
    'glg:kml-2.0-http-get-map': 'KML',     # google earth kml service (ver 2.0)
    'ogc:csw': 'CSW',                      # ogc-csw catalogue service for the web
    'ogc:kml': 'KML',                      # ogc-kml keyhole markup language
    'ogc:gml': 'GML',                      # ogc-gml geography markup language
    'ogc:wcs': 'WCS',                      # ogc-wcs web coverage service
    'ogc:wcs-1.1.0-http-get-capabilities': 'WCS',  # ogc-wcs web coverage service (ver 1.1.0)
    'ogc:wcts': 'WCTS',                    # ogc-wcts web coordinate transformation service
    'ogc:wfs': 'WFS',                      # ogc-wfs web feature service
    'ogc:wfs-1.0.0-http-get-capabilities': 'WFS',  # ogc-wfs web feature service (ver 1.0.0)
    'ogc:wfs-g': 'WFS',                    # ogc-wfs-g gazetteer service
    'ogc:wmc': 'WMC',                      # ogc-wmc web map context
    'ogc:wms': 'WMS',                      # ogc-wms web map service
    'ogc:wms-1.1.1-http-get-capabilities': 'WMS',  # ogc-wms capabilities service (ver 1.1.1)
    'ogc:wms-1.3.0-http-get-capabilities': 'WMS',  # ogc-wms capabilities service (ver 1.3.0)
    'ogc:wms-1.1.1-http-get-map': 'WMS',           # ogc web map service (ver 1.1.1)
    'ogc:wms-1.3.0-http-get-map': 'WMS',           # ogc web map service (ver 1.3.0)
    'ogc:wmts': 'WMTS',                           # ogc-wmts web map tiled service
    'ogc:wmts-1.0.0-http-get-capabilities': 'WMTS',  # ogc-wmts capabilities service (ver 1.0.0)
    'ogc:sos-1.0.0-http-get-observation': 'SOS',  # ogc-sos get observation (ver 1.0.0)
    'ogc:sos-1.0.0-http-post-observation': 'SOS', # ogc-sos get observation (post) (ver 1.0.0)
    'ogc:wns': 'WNS',                              # ogc-wns web notification service
    'ogc:wps': 'WPS',                              # ogc-wps web processing service
    'tms': 'TMS',                                  # tiled map service
    'www:download-1.0-ftp-download': 'FTP',        # file for download through ftp
    'www:download-1.0-http-download': 'HTTP',       # file for download
    'www:link-1.0-http-ical': 'ICAL',               # icalendar (url)
    'www:link-1.0-http-link': 'HTTP',               # web address (url)
    'www:link-1.0-http-partners': 'HTTP',           # partner web address (url)
    'www:link-1.0-http-related': 'HTTP',            # related link (url)
    'www:link-1.0-http-rss': 'HTTP',                # rss news feed (url)
    'www:link-1.0-http-samples': 'HTTP',            # showcase product (url)
    'www:link-1.0-http-opendap': 'HTTP',            # opendap url
    'web map service': 'WMS',
    'web feature service': 'WFS',
    'web coverage service': 'WCS',
    'web map tile service': 'WMTS',
    'html': 'HTML',
    'htm': 'HTML',
    'octet-stream': 'BINARY',
    'aspx': 'HTML',
    'www:download': 'HTTP',
    'www:link': 'HTTP',
    'application/octet-stream': 'BINARY',
    'application/html': 'HTML',
    'text/html': 'HTML',
    # Add other mappings as needed
}

FORMAT_STANDARDIZATION = {
    'format_patterns': {
        'wms': 'WMS',
        'web map service': 'WMS',
        'ogc:wms': 'WMS',
        'wfs': 'WFS',
        'web feature service': 'WFS',
        'ogc:wfs': 'WFS',
        'wmts': 'WMTS',
        'web map tile service': 'WMTS',
        'html': 'HTML',
        'htm': 'HTML',
        'binary': 'BINARY',
        'octet-stream': 'BINARY',
        'application/octet-stream': 'BINARY',
        'visor': 'HTML',
        'viewer': 'HTML',
        'enlace': 'HTML',
        'link': 'HTML',
        'html': 'HTML',
        'htm': 'HTML',
        'web': 'HTML',
    },
    'mimetype_mapping': {
        'WMS': 'application/vnd.ogc.wms_xml',
        'WFS': 'application/gml+xml',
        'WMTS': 'application/vnd.ogc.wmts+xml',
        'HTML': 'text/html',
        'BINARY': 'application/octet-stream',
    }
}

SERVICE_FORMAT = 'SERVICE'
API_FORMAT = 'API'
LINKED_DATA_SERVICE = "Linked Data Service"

FORMAT_MAPPING = {
    DOWNLOAD_PROTOCOL: ('FORMAT_FROM_PROTOCOL', 'FORMAT_FROM_PROTOCOL'),
    LINKED_DATA_PROTOCOL: ('FORMAT_FROM_PROTOCOL_IF_NOT_DATA', API_FORMAT),
    ESRI_REST_PROTOCOL: (SERVICE_FORMAT, API_FORMAT),
    APP_PROTOCOL: (SERVICE_FORMAT, API_FORMAT),
    MAP_PROTOCOL: (SERVICE_FORMAT, API_FORMAT),
    OGC_WMS_PROTOCOL: ('WMS', API_FORMAT),
    OGC_WFS_PROTOCOL: ('WFS', API_FORMAT),
    OGC_WMTS_PROTOCOL: ('WMTS', API_FORMAT),
    'OGC:WCS': ('WCS', API_FORMAT),
    'OGC:CSW': ('CSW', API_FORMAT),
    'OGC:SOS': ('SOS', API_FORMAT),
    'OGC:WCTS': ('WCTS', API_FORMAT),
    'WNS': ('WNS', API_FORMAT),
    'WPS': ('WPS', API_FORMAT),
    'TMS': ('TMS', API_FORMAT),
    'FTP': ('FTP', 'FTP'),
    'HTTP': ('HTTP', 'HTTP'),
    'ICAL': ('ICAL', 'ICAL'),
    # Add other mappings as needed
}

RESOURCE_TYPES = {
    'wms': ('/wms', 'service=wms', 'geoserver/wms', 'mapserver/wmsserver', 'com.esri.wms.Esrimap', 'service/wms'),
    'wfs': ('/wfs', 'service=wfs', 'geoserver/wfs', 'mapserver/wfsserver', 'com.esri.wfs.Esrimap'),
    'wcs': ('/wcs', 'service=wcs', 'geoserver/wcs', 'imageserver/wcsserver', 'mapserver/wcsserver'),
    'sos': ('/sos', 'service=sos'),
    'csw': ('/csw', 'service=csw'),
    'wmts': ('/wmts', 'service=wmts'),
    'kml': ('.kml', 'kml'),
    'kmz': ('.kmz',),
    'tms': ('/tms',),
    'esri_rest': ('arcgis/rest/services',),
}
    
FILE_TYPES = {
    'kml': ('kml',),
    'kmz': ('kmz',),
    'gml': ('gml',),
    'tif': ('tif', 'tiff'),
    'shp': ('shp',),
    'zip': ('zip',),
    'geojson': ('geojson', 'json'),
    'pdf': ('pdf',),
    'docx': ('docx', 'doc'),
    'pptx': ('pptx', 'ppt'),
    'xlsx': ('xlsx', 'xls'),
    'csv': ('csv',),
    'json': ('json',),
    'html': ('html', 'htm'),
    'xml': ('xml',),
    'geopackage': ('gpkg',),
    'sqlite': ('sqlite', 'db'),
    'exe': ('exe',),
    'bat': ('bat',),
    'sh': ('sh',),
    'zip': ('zip', 'rar', '7z', 'tar', 'gz', 'bz2'),
    'jpg': ('jpg', 'jpeg'),
    'png': ('png',),
    'gif': ('gif',),
    'tiff': ('tiff', 'tif'),
    'bmp': ('bmp',),
    'svg': ('svg',),
    'cad': ('dwg', 'dxf'),
    'kmz': ('kmz',),
    'gml': ('gml',),
    'txt': ('txt',),
    'rtf': ('rtf',),
    'odt': ('odt',),
    'ods': ('ods',),
    'odp': ('odp',),
    'ppt': ('ppt',),
    'xls': ('xls',),
    'doc': ('doc',),
    'pptm': ('pptm',),
    'xlsm': ('xlsm',),
    'dotx': ('dotx',),
    'potx': ('potx',),
    # Add other mappings as needed
}