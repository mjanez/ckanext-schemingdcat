from ckan.common import config
import ckan.logic as logic
from ckan import plugins as p
import logging
import os
import inspect
import json
import hashlib
from threading import Lock
import warnings
from functools import wraps

import yaml
from yaml.loader import SafeLoader
from pathlib import Path

from ckanext.dcat.utils import CONTENT_TYPES
from ckanext.scheming.helpers import (
    scheming_dataset_schemas,
)

from ckanext.schemingdcat import config as sdct_config

try:
    from paste.reloader import watch_file
except ImportError:
    watch_file = None

log = logging.getLogger(__name__)


_facets_dict = None
_public_dirs = None
_files_hash = []
_dirs_hash = []

_facets_dict_lock = Lock()
_public_dirs_lock = Lock()


def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used."""
    @wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn(f"Call to deprecated function {func.__name__}. This function will be removed in future versions.",
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    return new_func

def get_facets_dict():
    """Get the labels for all fields defined in the scheming file.

    Returns:
        dict: A dictionary containing the labels for all fields defined in the scheming file.
    """
    global _facets_dict
    if not _facets_dict:
        with _facets_dict_lock:
            if not _facets_dict:
                _facets_dict = {}

                schema = logic.get_action('scheming_dataset_schema_show')(
                    {},
                    {'type': 'dataset'}
                    )

                for item in schema['dataset_fields']:
                    _facets_dict[item['field_name']] = item['label']

                for item in schema['resource_fields']:
                    _facets_dict[item['field_name']] = item['label']

    return _facets_dict

def get_public_dirs():
    """Get the list of public directories specified in the configuration file.

    Returns:
        list: A list of public directories specified in the configuration file.
    """
    global _public_dirs

    if not _public_dirs:
        with _public_dirs_lock:
            if not _public_dirs:
                _public_dirs = config.get('extra_public_paths', '').split(',')

    return _public_dirs

def public_file_exists(path):
    """Check if a file exists in the public directories specified in the configuration file.

    Args:
        path (str): The path of the file to check.

    Returns:
        bool: True if the file exists in one of the public directories, False otherwise.
    """
    #log.debug("Check if exists: {0}".format(path))
    file_hash = hashlib.sha512(path.encode('utf-8')).hexdigest()

    if file_hash in _files_hash:
        return True

    public_dirs = get_public_dirs()
    for i in range(len(public_dirs)):
        public_path = os.path.join(public_dirs[i], path)
        if os.path.isfile(public_path):
            _files_hash.append(file_hash)
            return True

    return False

def public_dir_exists(path):
    """Check if a directory exists in the public directories specified in the configuration file.

    Args:
        path (str): The path of the directory to check.

    Returns:
        bool: True if the directory exists in one of the public directories, False otherwise.
    """
    dir_hash = hashlib.sha512(path.encode('utf-8')).hexdigest()

    if dir_hash in _dirs_hash:
        return True

    public_dirs = get_public_dirs()
    for i in range(len(public_dirs)):
        public_path = os.path.join(public_dirs[i], path)
        if os.path.isdir(public_path):
            _dirs_hash.append(dir_hash)
            return True

    return False

def init_config():
    sdct_config.linkeddata_links = _load_yaml('linkeddata_links.yaml')
    sdct_config.geometadata_links = _load_yaml('geometadata_links.yaml')
    sdct_config.endpoints = _load_yaml(sdct_config.endpoints_yaml)
    
    # Cache scheming schemas of local instance
    sdct_config.schemas = _get_schemas()
    sdct_config.form_tabs = set_schema_form_tabs()
    sdct_config.form_groups = set_schema_form_groups()

def is_yaml(file):
    """Check if a file has a YAML extension.

    Args:
        file (str): The file name or path.

    Returns:
        bool: True if the file has a .yaml or .yml extension, False otherwise.
    """
    return file.lower().endswith(('.yaml', '.yml'))

def _load_yaml(file):
    """Load a YAML file, either from a module path or a default directory.

    Args:
        file (str): The name of the YAML file to load. Can be a module path like "module:file.yaml".

    Returns:
        dict: A dictionary containing the data from the YAML file, or an empty dictionary if the file is invalid or cannot be loaded.
    """
    if not is_yaml(file):
        log.error("The file {0} is not a valid YAML file".format(file))
        return {}

    yaml_data = _load_yaml_module_path(file)
    if not yaml_data:
        yaml_data = _load_default_yaml(file)
    return yaml_data

def _load_yaml_module_path(file):
    """Load a YAML file from a module path.

    Given a path like "module:file.yaml", find the file relative to the import path of the module.

    Args:
        file (str): The module path of the YAML file.

    Returns:
        dict or None: A dictionary containing the data from the YAML file, or None if the module cannot be imported or the file cannot be loaded.
    """
    
    if ':' not in file:
        return None

    module, file_name = file.split(':', 1)
    try:
        m = __import__(module, fromlist=[''])
    except ImportError:
        log.error("Module {0} could not be imported".format(module))
        return None

    return _load_yaml_file(os.path.join(os.path.dirname(inspect.getfile(m)), file_name))

def _load_default_yaml(file):
    """Load a YAML file from the 'codelists' directory of the schemingdcat extension.

    Args:
        file (str): The name of the YAML file to load.

    Returns:
        dict: A dictionary containing the data from the YAML file, or an empty dictionary if the file cannot be loaded.
    """
    source_path = Path(__file__).resolve(True)
    return _load_yaml_file(source_path.parent.joinpath('codelists', file))

def _load_yaml_file(path):
    """Load a YAML file from a given path.

    Args:
        path (str): The file path of the YAML file.

    Returns:
        dict: A dictionary containing the data from the YAML file, or an empty dictionary if the file cannot be loaded.
    """
    yaml_data = {}
    try:
        if os.path.exists(path):
            if watch_file:
                watch_file(path)
            with open(path, 'r') as f:
                yaml_data = yaml.load(f, Loader=SafeLoader)
        else:
            log.error("The file {0} does not exist".format(path))
    except Exception as e:
        log.error("Could not read configuration from {0}: {1}".format(path, e))
    return yaml_data

def get_linked_data(id):
    """Get linked data for a given identifier.

    Args:
        id (str): The identifier to get linked data for.

    Returns:
        list: A list of dictionaries containing linked data for the identifier.
    """
    if sdct_config.debug:
        linkeddata_links = _load_yaml('linkeddata_links.yaml')
    else:
        linkeddata_links = sdct_config.linkeddata_links

    data=[]
    for name in CONTENT_TYPES:
        data.append({
            'name': name,
            'display_name': linkeddata_links.get(name,{}).get('display_name',CONTENT_TYPES[name]),
            'image_display_url': linkeddata_links.get(name,{}).get('image_display_url', None),
            'description': linkeddata_links.get(name,{}).get('description','Formats '+ CONTENT_TYPES[name]),
            'description_url': linkeddata_links.get(name,{}).get('description_url', None),
            'endpoint_data':{
                '_id': id,
                '_format': name,
                }
        })

    return data

def get_geospatial_metadata():
    """Get geospatial metadata for CSW formats.

    Returns:
        list: A list of dictionaries containing geospatial metadata for CSW formats.
    """
    if sdct_config.debug:
        geometadata_links = _load_yaml('geometadata_links.yaml')
    else:
        geometadata_links = sdct_config.geometadata_links
    data=[]
    for item in geometadata_links.get('csw_formats',{}):
        data.append({
            'name': item['name'],
            'display_name': item['display_name'],
            'image_display_url': item['image_display_url'],
            'description': item['description'],
            'description_url': item['description_url'],
            'url': (sdct_config.geometadata_link_domain or '') + geometadata_links['csw_url'].format(output_format=item['output_format'], schema=item['output_schema'], id='{id}')
        })

    return data

def parse_json(value, default_value=None):
    """
    Parses a JSON string and returns the resulting object.
    If the input value is not a valid JSON string, returns the default value.
    If the default value is not provided, returns the input value.

    Args:
        value (str): The JSON string to parse.
        default_value (any, optional): The default value to return if the input value is not a valid JSON string.
            Defaults to None.

    Returns:
        any: The parsed JSON object, or the default value if the input value is not a valid JSON string.
    """
    try:
        return json.loads(value)
    except (ValueError, TypeError, AttributeError):
        if default_value is not None:
            return default_value

        # The json may already have been parsed and we have the value for the
        # language already.
        if isinstance(value, int):
            # If the value is a number, it has been converted into an int - but
            # we want a string here.
            return str(value)
        return value
    
def _get_schemas():
    """
    Fetches the dataset schemas using the scheming_dataset_schemas function.

    This function attempts to retrieve the dataset schemas. If a KeyError is encountered,
    it logs the error and returns an empty dictionary.

    Returns:
        dict: The dataset schemas if successfully retrieved, otherwise an empty dictionary.

    Raises:
        KeyError: If there is an issue accessing the dataset schemas.
    """
    try:
        return scheming_dataset_schemas()
    except KeyError as e:
        log.error('KeyError encountered while fetching dataset schemas: %s', e)
        return {}
    
def set_schema_form_tabs():
    """
    Sets the schema form tabs for each dataset type in the `sdct_config.schemas`.

    This function iterates over the schemas defined in `sdct_config.schemas` and sets the corresponding
    form tabs in `sdct_config.form_tabs`. If a schema does not have `schema_form_tabs`, it sets the form tab to None.
    Logs warnings and errors as appropriate.

    Raises:
        KeyError: If there is an issue accessing the schema form tabs.
    """
    if not sdct_config.schemas:
        log.warning('sdct_config.schemas is empty, no local scheming.dataset_schemas loaded.')
        return

    form_tabs = {}

    for dataset_type, schema in sdct_config.schemas.items():
        try:
            form_tabs[dataset_type] = schema.get('schema_form_tabs', None)
        except p.toolkit.ObjectNotFound:
            pass
        except KeyError as e:
            log.error('KeyError encountered while setting schema form tabs for dataset_type: %s, error: %s', dataset_type, e)
            
    return form_tabs     

def set_schema_form_groups():
    """
    Sets the schema form groups for each dataset type in the `sdct_config.schemas`.

    This function iterates over the schemas defined in `sdct_config.schemas` and sets the corresponding
    form tabs in `sdct_config.form_groups`. If a schema does not have `schema_form_groups`, it sets the form tab to None.
    Logs warnings and errors as appropriate.

    Raises:
        KeyError: If there is an issue accessing the schema form tabs.
    """
    if not sdct_config.schemas:
        log.warning('sdct_config.schemas is empty, no local scheming.dataset_schemas loaded.')
        return

    form_groups = {}

    for dataset_type, schema in sdct_config.schemas.items():
        try:
            form_groups[dataset_type] = schema.get('schema_form_groups', None)
        except p.toolkit.ObjectNotFound:
            pass
        except KeyError as e:
            log.error('KeyError encountered while setting schema form tabs for dataset_type: %s, error: %s', dataset_type, e)
            
    return form_groups     