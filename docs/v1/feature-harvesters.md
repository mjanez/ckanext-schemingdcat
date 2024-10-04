## Harvesters
### Basic using
In production, when `gather` and `consumer` processes are running, the following command are used to start and stop the background processes:

  - `ckan harvester run`: Starts any harvest jobs that have been created by putting them onto
    the gather queue. Also checks running jobs - if finished it
    changes their status to Finished.

To testing harvesters in development, you can use the following command:
  - `ckan harvester run-test {source-id/name}`: This does all the stages of the harvest (creates job, gather, fetch, import) without involving the web UI or the queue backends. This is useful for testing a harvester without having to fire up gather/fetch_consumer processes, as is done in production.

!!! warning
    
    After running the `run-test` command, you should stop all background processes for `gather` and `consumer` to avoid conflicts.


### Scheming DCAT CKAN Harvester: CKAN Harvester for custom schemas
The plugin includes a harvester for remote CKAN instances using the custom schemas provided by `schemingdcat` and `ckanext-scheming`. This harvester is a subclass of the CKAN Harvester provided by `ckanext-harvest` and is designed to work with the `schemingdcat` plugin to provide a more versatile and customizable harvester for CKAN instances.

To use it, you need to add the `schemingdcat_ckan_harvester` plugin to your options file:

  ```ini
    ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_ckan_harvester
  ```

The Scheming DCAT CKAN Harvester supports the same configuration options as the [CKAN Harvester](https://github.com/ckan/ckanext-harvest#the-ckan-harvester), plus the following additional options:

* `dataset_field_mapping/distribution_field_mapping` (Optional):  Mapping field names from local to remote instance, all info at: [CKAN Harvester Field mapping structure](#field-mapping-structure)
* `field_mapping_schema_version` (**Mandatory if exists** `dataset_field_mapping/distribution_field_mapping`): Schema version of the field_mapping to ensure compatibility with older schemas. The default is `2`.
* `schema` (Optional): The name of the schema to use for the harvested datasets. This is the `schema_name` as defined in the scheming file. The remote and local instances must have the same dataset schema. If not provided, the `dataset_field_mapping/distribution_field_mapping` is needed to mapping fields.
* `allow_harvest_datasets` (Optional): If `true`, the harvester will create new records even if the package type is from the harvest source. If `false`, the harvester will only create records that originate from the instance. Default is `false`.
* `remote_orgs` (Optional): [WIP]. Only `only_local`.
* `remote_groups` (Optional): [WIP]. Only `only_local`.
* `clean_tags`: By default, tags are stripped of accent characters, spaces and capital letters for display. Setting this option to `False` will keep the original tag names. Default is `True`.

And example configuration might look like this:

  ```json
      {
      "api_version": 2,
      "clean_tags": false,
      "default_tags": [{"name": "inspire"}, {"name": "geodcatap"}],
      "default_groups": ["transportation", "hb"],
      "default_extras": {"encoding":"utf8", "harvest_description":"Harvesting from Sample Catalog", "harvest_url": "{harvest_source_url}/dataset/{dataset_id}"},
      "organizations_filter_include": ["remote-organization"],
      "groups_filter_include":[],
      "override_extras":false,
      "user":"harverster-user",
      "api_key":"<REMOTE_API_KEY>",
      "read_only": true,
      "remote_groups": "only_local",
      "remote_orgs": "only_local",
      "schema": "geodcatap",
      "allow_harvest_datasets":false,
      "field_mapping_schema_version":2,
      "dataset_field_mapping": {
        "title": {
            "field_name": "my_title"
          },
        "title_translated": {
            "languages": {
                "en": {
                    "field_name": "my_title-en"
                },
                "es": {
                    "field_name": "my_title"
                }
            }
        },
        "private": {
            "field_name": "private"
        },
        "tag_string": {
            "field_name": ["theme_a", "theme_b", "theme_c"]
        },
        "theme_es": {
            "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
        },
        "tag_uri": {
            "field_name": "keyword_uri",
            // "field_value" extends the original list of values retrieved from the remote file for all records.
            "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
        },
        "my_custom_field": {
            // If you need to map a field in a remote dict to the "extras" dict, use the "extras_" prefix to indicate that the field is there.
            "field_name": "extras_remote_custom_field"
        },
      },
      }
  ```
#### Field mapping structure
The `dataset_field_mapping`/`distribution_field_mapping` is structured as follows (multilingual version):

```json
{
  ...
  "field_mapping_schema_version": 2,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      "languages": {
        "<language>":  {
          <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<excel_field_name>/<excel_field_name_list>">
        },
        ...
      },
      ...
    },
    ...
  }
}
```

* `<schema_field_name>`: The name of the field in the CKAN schema.
  * `<language>`: (Optional) The language code for multilingual fields. This should be a valid [ISO 639-1 language code](https://localizely.com/iso-639-1-list/). This is now nested under the `languages` key.
* `<fixed_value>/<fixed_value_list>`: (Optional) A fixed value or a list of fixed values that will be assigned to the field for all records.
* **Field labels**: Field name:
  * `<field_name>/<field_name_list>`: (Optional) The name of the field in the remote file or a list of field names.

For fields that are not multilingual, you can directly use `field_name` without the `languages` key. For example:

```json
{
  ...
  "field_mapping_schema_version": 2,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<excel_field_name>/<excel_field_name_list>">
    },
    ...
  }
}
```

!!! info

  The field mapping can be done either at the dataset level using `dataset_field_mapping` or at the resource level using `distribution_field_mapping`. The structure and options are the same for both. The `field_mapping_schema_version` is `2` by default, but needs to be set to avoid errors.

#### Field Types
There are two types of fields that can be defined in the configuration:

1. **Regular fields**: These fields have a field label to define the mapping or a fixed value for all its records.
    - **Properties**: A field can have one of these three properties:
      - **Fixed value fields (`field_value`)**: These fields have a fixed value that is assigned to all records. This is defined using the `field_value` property. If `field_value` is a list, `field_name` could be set at the same time, and the `field_value` extends the list obtained from the remote field.
      - **Field labels**: Field name:
        - **Name based fields (`field_name`)**: These fields are defined by their name in the Excel file. This is defined using the `field_name` property, or if you need to map a field in a remote dict to the `extras` dict, use the `extras_` prefix to indicate that the field is there.
2. **Multilingual Fields (`languages`)**: These fields have different values for different languages. Each language is represented as a separate object within the field object (`es`, `en`, ...). The language object can have `field_value` and `field_name` properties, just like a normal field.


**Example**
Here are some examples of configuration files:

  * *Field names*: With `field_name` to define the mapping based on names of attributes in the remote sheet (`my_title`, `org_identifier`, `keywords`).

  ```json
  {
    "api_version": 2,
    "clean_tags": false,

    ...
    # other properties
    ...

    "field_mapping_schema_version": 2,
    "dataset_field_mapping": {
      "title": {
          "field_name": "my_title"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_name": "my_title-en"
              },
              "de": {
                  "field_value": ""
              },
              "es": {
                  "field_name": "my_title"
              }
          }
      },
      "private": {
          "field_name": "private"
      },
      "theme": {
          "field_name": ["theme", "theme_eu"]
      },
      "tag_custom": {
          "field_name": "keywords"
      },
      "tag_string": {
          "field_name": ["theme_a", "theme_b", "theme_c"]
      },
      "theme_es": {
          "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
      },
      "tag_uri": {
          "field_name": "keyword_uri",
          // "field_value" extends the original list of values retrieved from the remote file for all records.
          "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
      },
      "my_custom_field": {
          // If you need to map a field in a remote dict to the "extras" dict, use the "extras_" prefix to indicate that the field is there.
          "field_name": "extras_remote_custom_field"
      }
    }
  }
  ```

###TODO: Scheming DCAT CSW INSPIRE Harvester
A harvester for remote CSW catalogues using the INSPIRE ISO 19139 metadata profile. This harvester is a subclass of the CSW Harvester provided by `ckanext-spatial` and is designed to work with the `schemingdcat` plugin to provide a more versatile and customizable harvester for CSW endpoints and GeoDCAT-AP CKAN instances.

To use it, you need to add the `schemingdcat_csw_harvester` plugin to your options file:

  ```ini
    ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_csw_harvester
  ```


### Remote Google Sheet/Onedrive Excel metadata upload Harvester
A harvester for remote [Google spreadsheets](https://docs.gspread.org/en/v6.0.0/oauth2.html) and Onedrive Excel files with Metadata records. This harvester is a subclass of the Scheming DCAT Base Harvester provided by `ckanext-schemingdcat` to provide a more versatile and customizable harvester for Excel files that have metadata records in them.

To use it, you need to add the `schemingdcat_xls_harvester` plugin to your options file:

  ```ini
  ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_xls_harvester
  ```

Remote Google Sheet/Onedrive Excel metadata upload Harvester supports the following options:

* `storage_type` - **Mandatory**: The type of storage to use for the harvested datasets as `onedrive` or `gspread`. Default is `onedrive`.
* `dataset_sheet` - **Mandatory**: The name of the sheet in the Excel file that contains the dataset records.
* `field_mapping_schema_version`: Schema version of the field_mapping to ensure compatibility with older schemas. The default is `2`.
* `dataset_field_mapping/distribution_field_mapping`:  Mapping field names from local to remote instance, all info at: [Field mapping structure](#field-mapping-structure-sheets-harvester)
* `credentials`: The `credentials` parameter should be used to provide the authentication credentials. The credentials depends on the `storage_type` used. 
  * For `onedrive`: The credentials parameter should be a dictionary with the following keys: `username`: A string representing the username. `password`: A string representing the password.
  * For `gspread` or `gdrive`: The credentials parameter should be a string containing the credentials in `JSON` format. You can obtain the credentials by following the instructions provided in the [Google Workspace documentation.](https://developers.google.com/workspace/guides/create-credentials?hl=es-419)
* `distribution_sheet`: The name of the sheet in the Excel file that contains the distribution records. If not provided, the harvester will only create records for the dataset sheet.
* `datadictionary_sheet`: The name of the sheet in the Excel file that contains the data dictionary records. If not provided, the harvester will only create records for the dataset sheet.
* `api_version`: You can force the harvester to use either version 1 or 2 of the CKAN API. Default is `2`.
* `default_tags`: A list of tags that will be added to all harvested datasets. Tags don't need to previously exist. This field takes a list of tag dicts which allows you to optionally specify a vocabulary. Default is `[]`.
* `default_groups`: A list of group IDs or names to which the harvested datasets will be added to. The groups must exist in the local instance. Default is `[]`.
* `default_extras`: A dictionary of key value pairs that will be added to extras of the harvested datasets. You can use the following replacement strings, that will be replaced before creating or updating the datasets:
    * `{dataset_id}`
    * `{harvest_source_id}`
    * `{harvest_source_url}` Will be stripped of trailing forward slashes (/)
    * `{harvest_source_title}`
    * `{harvest_job_id}`
    * `{harvest_object_id}`
* `override_extras`: Assign default extras even if they already exist in the remote dataset. Default is `False` (only non existing extras are added).
* `user`: User who will run the harvesting process. Please note that this user needs to have permission for creating packages, and if default groups were defined, the user must have permission to assign packages to these groups.
* `read_only`: Create harvested packages in read-only mode. Only the user who performed the harvest (the one defined in the previous setting or the 'harvest' sysadmin) will be able to edit and administer the packages created from this harvesting source. Logged in users and visitors will be only able to read them.
* `force_all`: By default, after the first harvesting, the harvester will gather only the modified packages from the remote site since the last harvesting Setting this property to true will force the harvester to gather all remote packages regardless of the modification date. Default is `False`.
* `clean_tags`: By default, tags are stripped of accent characters, spaces and capital letters for display. Setting this option to `False` will keep the original tag names. Default is `True`.
* `source_date_format`: By default the harvester uses [`dateutil`](https://dateutil.readthedocs.io/en/stable/parser.html) to parse the date, but if the date format of the strings is particularly different you can use this parameter to specify the format, e.g. `%d/%m/%Y`. Accepted formats are: [COMMON_DATE_FORMATS](https://github.com/mjanez/ckanext-schemingdcat/blob/main/ckanext/schemingdcat/config.py#L185-L200)

#### Field mapping structure (Sheets harvester)
The `dataset_field_mapping`/`distribution_field_mapping` is structured as follows (multilingual version):

```json
{
  ...
  "field_mapping_schema_version": 2,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      "languages": {
        "<language>":  {
          <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<excel_field_name>/<excel_field_name_list>">/< "field_position": "<excel_column>/<excel_column_list>">
        },
        ...
      },
      ...
    },
    ...
  }
}
```

* `<schema_field_name>`: The name of the field in the CKAN schema.
  * `<language>`: (Optional) The language code for multilingual fields. This should be a valid [ISO 639-1 language code](https://localizely.com/iso-639-1-list/). This is now nested under the `languages` key.
* `<fixed_value>/<fixed_value_list>`: (Optional) A fixed value or a list of fixed values that will be assigned to the field for all records.
* **Field labels**: Field position or field name:
  * `<field_position>/<field_position_list>`: (Optional) The position of the field in the remote file, represented as a letter or a list of letters (e.g., "A", "B", "C").
  * `<field_name>/<field_name_list>`: (Optional) The name of the field in the remote file or a list of field names.

For fields that are not multilingual, you can directly use `field_name` or `field_position` without the `languages` key. For example:

```json
{
  ...
  "field_mapping_schema_version": 2,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<excel_field_name>/<excel_field_name_list>">/< "field_position": "<excel_column>/<excel_column_list>">
    },
    ...
  }
}
```

!!! info

  The field mapping can be done either at the dataset level using `dataset_field_mapping` or at the resource level using `distribution_field_mapping`. The structure and options are the same for both. The `field_mapping_schema_version` is `2` by default, but needs to be set to avoid errors.

#### Field Types
There are two types of fields that can be defined in the configuration:

1. **Regular fields**: These fields have a field label/position to define the mapping or a fixed value for all its records.
    - **Properties**: A field can have one of these three properties:
      - **Fixed value fields (`field_value`)**: These fields have a fixed value that is assigned to all records. This is defined using the `field_value` property. If `field_value` is a list, `field_name` or `field_position` could be set at the same time, and the `field_value` extends the list obtained from the remote field.
      - **Field labels**: Field position or field name:
        - **Position based fields (`field_position`)**: These fields are defined by their position in the Excel file. This is defined using the `field_position` property.
        - **Name based fields (`field_name`)**: These fields are defined by their name in the Excel file. This is defined using the `field_name` property.
2. **Multilingual Fields (`languages`)**: These fields have different values for different languages. Each language is represented as a separate object within the field object (`es`, `en`, ...). The language object can have `field_value`, `field_position` and `field_name` properties, just like a normal field.


**Example**
Here are some examples of configuration files:

* *Field positions*: With `field_position` to define the mapping based on positions of attributes in the remote sheet (`A`, `B`, `AA`, etc.).
  ```json
  {
    "storage_type": "gspread",
    "dataset_sheet": "Dataset",
    "distribution_sheet": "Distribution",

    ...
    # other properties
    ...

    "field_mapping_schema_version": 2,
    "dataset_field_mapping": {
      "title": {
          "field_position": "A"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_position": "AC"
              },
              "de": {
                  "field_value": ""
              },
              "es": {
                  "field_position": "A"
              }
          }
      },
      "private": {
          "field_position": "F"
      },
      "theme": {
          "field_position": ["G", "AA"],
      },
      "tag_custom": {
          "field_position": "B"
      },
      "tag_string": {
          "field_position": ["A", "B", "AC"]
      },
      "theme_es": {
          "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
      },
      "tag_uri": {
          "field_position": "Z",
          // "field_value" extends the original list of values retrieved from the remote file for all records.
          "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
      },
    }
  }
  ```

  * *Field names*: With `field_name` to define the mapping based on names of attributes in the remote sheet (`my_title`, `org_identifier`, `keywords`).

  ```json
  {
    "storage_type": "gspread",
    "dataset_sheet": "Dataset",
    "distribution_sheet": "Distribution",

    ...
    # other properties
    ...

    "field_mapping_schema_version": 2,
    "dataset_field_mapping": {
      "title": {
          "field_name": "my_title"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_name": "my_title-en"
              },
              "de": {
                  "field_value": ""
              },
              "es": {
                  "field_name": "my_title"
              }
          }
      },
      "private": {
          "field_name": "private"
      },
      "theme": {
          "field_name": ["theme", "theme_eu"]
      },
      "tag_custom": {
          "field_name": "keywords"
      },
      "tag_string": {
          "field_name": ["theme_a", "theme_b", "theme_c"]
      },
      "theme_es": {
          "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
      },
      "tag_uri": {
          "field_name": "keyword_uri",
          // "field_value" extends the original list of values retrieved from the remote file for all records.
          "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
      },
    }
  }
  ```

!!! info
  
  All `*_translated` fields need their fallback `non-suffix` field as simple field, e.g: 
   ```json
   ...
      "title": {
           "field_position": "A"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_value": ""
              },
              "es": {
                  "field_position": "A"
              }
         }
      },
   ...
  ```

##TODO: CLI
The `ckan schemingdcat` command offers utilites:

    ckan schemingdcat create-inspire-tags -l es

    ckan schemingdcat download-rdf-eu-vocabs

