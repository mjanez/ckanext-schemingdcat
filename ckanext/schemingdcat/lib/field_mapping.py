import re

class FieldMappingValidator:
    """
    This class validates field mapping configurations in a data schema. It checks the validity of language codes, language configuration properties and field settings. Throws an error if invalid configurations are found.
    """
    def __init__(self):
        """
        Initialize FieldMappingValidator with a set of valid properties.
        """
        self.valid_props = {'field_value', 'field_position', 'field_name', 'languages'}
        self.validators = {
            1: self.validate_v1,
            2: self.validate_v2
        }

    def _check_value(self, local_field, prop, value):
        """
        Check if the value is valid.

        Args:
            local_field (str): The local field name.
            prop (str): The property name.
            value (str or list): The value to check.

        Raises:
            ValueError: If the value is not valid.
        """
        if not isinstance(value, (list, str)):
            raise ValueError(f'"{local_field}" (property: "{prop}") must be a string or a list: "value_1" or ["value_1", "value_2"]')
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError(f'"{local_field}" (property: "{prop}") must be a list of strings: "["value_1", "value_2"]')
        elif isinstance(value, str):
                if ',' in value and prop != 'field_value':
                    raise ValueError(f'"{local_field}" (property: "{prop}") must not contain commas. Use a list ["value_1", "value_2"] instead of a comma-separated string: "value_1,value_2"')

    def _check_non_translated_fields(self, field_mapping):
        """
        Check for corresponding non-translated fields.

        Args:
            field_mapping (dict): The field mapping to validate.

        Raises:
            ValueError: If a non-translated field corresponding to a translated field exists.
        """
        for field in field_mapping.keys():
            if field.endswith('_translated') and field[:-11] in field_mapping:
                raise ValueError(f'Field "{field[:-11]}" is not required if "{field}" exists.')

    def validate(self, field_mapping, schema_version=None):
        """
        Validate the field mapping for the given schema version.

        Args:
            field_mapping (dict): The field mapping to validate.
            schema_version (int, optional): The schema version. Defaults to the latest version.

        Raises:
            ValueError: If the field mapping is not valid.
        """
        
        if schema_version is None:
            schema_version = max(self.validators.keys())

        validator = self.validators.get(schema_version)
        if validator is None:
            raise ValueError(f'Unsupported schema version: {schema_version}. Supported versions are: {list(self.validators.keys())}')

        validator(field_mapping)

    def validate_v1(self, field_mapping):
        """
        Validate the field mapping for version 1.

        Args:
            field_mapping (dict): The field mapping to validate.

        Raises:
            ValueError: If the field mapping is not valid.
        """

        self._check_non_translated_fields(field_mapping)

        for local_field, remote_field in field_mapping.items():
            if not isinstance(local_field, str):
                raise ValueError('"local_field_name" must be a string')
            if not isinstance(remote_field, (str, dict)):
                raise ValueError('"remote_field_name" must be a string or a dictionary')
            if isinstance(remote_field, dict):
                for lang, remote_field_name in remote_field.items():
                    if not isinstance(lang, str) or not isinstance(remote_field_name, str):
                        raise ValueError('In translated fields, both language and remote_field_name must be strings. e.g. "notes_translated": {"es": "notes-es"}')
                    if not re.match("^[a-z]{2}$", lang):
                        raise ValueError('Language code must be a 2-letter ISO 639-1 code')
                    
    def validate_v2(self, field_mapping):
        """
        Validate the field mapping for version 2.

        Args:
            field_mapping (dict): The field mapping to validate.

        Raises:
            ValueError: If the field mapping is not valid.
        """
        field_position_defined = False
        field_name_defined = False
        field_value_defined = False

        self._check_non_translated_fields(field_mapping)

        for local_field, field_config in field_mapping.items():
            if not isinstance(local_field, str):
                raise ValueError('"local_field_name" must be a string')
            if not isinstance(field_config, dict):
                raise ValueError('"field_config" must be a dictionary')

            for prop, value in field_config.items():
                if prop not in self.valid_props:
                    raise ValueError(f'Invalid property "{prop}" in *_field_mapping. Check: https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure')
                if prop == 'field_position':
                    field_position_defined = True
                    self._check_value(local_field, prop, value)
                if prop == 'field_name':
                    field_name_defined = True
                    self._check_value(local_field, prop, value)
                if prop == 'field_value':
                    field_value_defined = True
                    self._check_value(local_field, prop, value)
                if prop == 'languages':
                    if not isinstance(value, dict):
                        raise ValueError('"languages" must be a dictionary')
                    for lang, lang_config in value.items():
                        if not isinstance(lang, str) or not re.match("^[a-z]{2}$", lang):
                            raise ValueError('Language code must be a 2-letter ISO 639-1 code')
                        if not isinstance(lang_config, dict):
                            raise ValueError('Language config must be a dictionary')
                        for lang_prop, lang_value in lang_config.items():
                            if lang_prop not in self.valid_props:
                                raise ValueError(f'Invalid property "{lang_prop}" in language config')
                            if not isinstance(lang_value, (str)):
                                raise ValueError(f'"{lang_prop}" must be a string')

        if field_position_defined and field_name_defined:
            raise ValueError(f'Both "field_position" and "field_name" cannot be defined in the field mapping. Define either all as "field_position" or all as "field_name". "local_field_name" with errors: "{local_field}"')

        if (field_position_defined or field_name_defined) and field_value_defined:
            if field_config.get('field_position') is not None or field_config.get('field_name') is not None:
                if not isinstance(field_config.get('field_value'), list):
                    raise ValueError(f'"field_value" for "{local_field}" can only be used if it is a list. First, check that the local_field_name accepts lists, otherwise the harvester validator may have problems.')