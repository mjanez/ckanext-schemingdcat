import sys
import logging

from ckan.common import json
from ckan.lib.plugins import DefaultTranslation
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import unflatten

from ckanext.scheming.plugins import (
    SchemingDatasetsPlugin,
    SchemingGroupsPlugin,
    SchemingOrganizationsPlugin,
    _field_validators,
    _field_output_validators,
    _field_create_validators,
    expand_form_composite,
)
from ckanext.scheming import logic as scheming_logic
from ckanext.scheming import validation as scheming_validation

import ckanext.schemingdcat.cli as cli
import ckanext.schemingdcat.config as sdct_config
from ckanext.schemingdcat.faceted import Faceted
from ckanext.schemingdcat.utils import init_config
from ckanext.schemingdcat.package_controller import PackageController
from ckanext.schemingdcat import helpers, validators, logic, blueprint, subscriptions


log = logging.getLogger(__name__)


convert_to_extras = toolkit.get_converter('convert_to_extras')

class SchemingDCATPlugin(
    plugins.SingletonPlugin, Faceted, PackageController, DefaultTranslation
):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ISignal)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")

        # toolkit.add_resource('fanstatic',
        #                     'schemingdcat')

        toolkit.add_resource("assets", "ckanext-schemingdcat")

        sdct_config.default_locale = config_.get(
            "ckan.locale_default", sdct_config.default_locale
        )

        sdct_config.default_facet_operator = config_.get(
            "schemingdcat.default_facet_operator", sdct_config.default_facet_operator
        )

        sdct_config.icons_dir = config_.get(
            "schemingdcat.icons_dir", sdct_config.icons_dir
        )

        sdct_config.organization_custom_facets = toolkit.asbool(
            config_.get(
                "schemingdcat.organization_custom_facets",
                sdct_config.organization_custom_facets,
            )
        )

        sdct_config.group_custom_facets = toolkit.asbool(
            config_.get(
                "schemingdcat.group_custom_facets", sdct_config.group_custom_facets
            )
        )
        
        sdct_config.default_package_item_icon = config_.get(
                "schemingdcat.default_package_item_icon", sdct_config.default_package_item_icon
            ) or sdct_config.default_package_item_icon

        sdct_config.default_package_item_show_spatial = toolkit.asbool(
            config_.get(
                "schemingdcat.default_package_item_show_spatial", sdct_config.default_package_item_show_spatial
            )
        )

        sdct_config.show_metadata_templates_toolbar = toolkit.asbool(
            config_.get(
                "schemingdcat.show_metadata_templates_toolbar", sdct_config.show_metadata_templates_toolbar
            )
        )
        
        sdct_config.metadata_templates_search_identifier = config_.get(
                "schemingdcat.metadata_templates_search_identifier", sdct_config.metadata_templates_search_identifier
            ) or sdct_config.metadata_templates_search_identifier
        
        sdct_config.endpoints_yaml = config_.get(
            "schemingdcat.endpoints_yaml", sdct_config.endpoints_yaml
            ) or sdct_config.endpoints_yaml

        sdct_config.debug = toolkit.asbool(config_.get("debug", sdct_config.debug))
        
        # Default value use local ckan instance with /csw
        sdct_config.geometadata_base_uri = config_.get(
            "schemingdcat.geometadata_base_uri", "/csw"
        )

        # Social accounts
        sdct_config.social_github = helpers.schemingdcat_check_valid_url(
            config_.get(
            "schemingdcat.social_github"
            ) 
        ) or sdct_config.social_github
        
        sdct_config.social_x = helpers.schemingdcat_check_valid_url(
            config_.get(
            "schemingdcat.social_x"
            ) 
        ) or sdct_config.social_x
        
        sdct_config.social_linkedin = helpers.schemingdcat_check_valid_url(
            config_.get(
            "schemingdcat.social_linkedin"
            ) 
        ) or sdct_config.social_linkedin

        # Load yamls config files
        init_config()

        # Update the site statistics
        # Check whether we are running a database initialization or upgrade command.
        # If so, we should skip the statistics update to avoid potential conflicts.
        args = sys.argv
        if 'db' in args and ('init' in args or 'upgrade' in args):
            log.warning('Skipping Open Data site stats update due to db init or upgrade.')
        else:
            log.debug('Initializing Open Data site statistics')
            helpers.schemingdcat_update_open_data_statistics()

        # configure Faceted class (parent of this)
        self.facet_load_config(config_.get("schemingdcat.facet_list", "").split())

    def get_helpers(self):
        respuesta = dict(helpers.all_helpers)
        return respuesta

    def get_validators(self):
        return dict(validators.all_validators)

    # IBlueprint
    def get_blueprint(self):
        return [blueprint.schemingdcat]

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # ISignal
    def get_signal_subscriptions(self):
        return subscriptions.get_subscriptions()

class SchemingDCATDatasetsPlugin(SchemingDatasetsPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)

    def read_template(self):
        return "schemingdcat/package/read.html"

    def resource_template(self):
        return "schemingdcat/package/resource_read.html"

    def package_form(self):
        return "schemingdcat/package/snippets/package_form.html"

    def resource_form(self):
        return "schemingdcat/package/snippets/resource_form.html"

    def get_actions(self):
        return {
            "schemingdcat_dataset_schema_name": logic.schemingdcat_dataset_schema_name,
            "scheming_dataset_schema_list": scheming_logic.scheming_dataset_schema_list,
            "scheming_dataset_schema_show": scheming_logic.scheming_dataset_schema_show,
        }

    # Override Scheming plugin to avoid errors when not extras are present in datastore resource (for ex in data_dict['extras'] KeyError: 'extras')
    def validate(self, context, data_dict, schema, action):
        """
        Validate and convert for package_create, package_update and
        package_show actions.
        """
        thing, action_type = action.split('_')
        t = data_dict.get('type')
        if not t or t not in self._schemas:
            return data_dict, {'type': [
                "Unsupported dataset type: {t}".format(t=t)]}

        scheming_schema = self._expanded_schemas[t]

        before = scheming_schema.get('before_validators')
        after = scheming_schema.get('after_validators')
        if action_type == 'show':
            get_validators = _field_output_validators
            before = after = None
        elif action_type == 'create':
            get_validators = _field_create_validators
        else:
            get_validators = _field_validators

        if before:
            schema['__before'] = scheming_validation.validators_from_string(
                before, None, scheming_schema)
        if after:
            schema['__after'] = scheming_validation.validators_from_string(
                after, None, scheming_schema)
        fg = (
            (scheming_schema['dataset_fields'], schema, True),
            (scheming_schema['resource_fields'], schema['resources'], False)
        )

        composite_convert_fields = []
        for field_list, destination, is_dataset in fg:
            for f in field_list:
                convert_this = is_dataset and f['field_name'] not in schema
                destination[f['field_name']] = get_validators(
                    f,
                    scheming_schema,
                    convert_this
                )
                if convert_this and 'repeating_subfields' in f:
                    composite_convert_fields.append(f['field_name'])

        def composite_convert_to(key, data, errors, context):
            unflat = unflatten(data)
            for f in composite_convert_fields:
                if f not in unflat:
                    continue
                data[(f,)] = json.dumps(unflat[f], default=lambda x:None if x == toolkit.missing else x)
                convert_to_extras((f,), data, errors, context)
                del data[(f,)]

        if action_type == 'show':
            if composite_convert_fields and 'extras' in data_dict:
                for ex in data_dict['extras']:
                    if ex['key'] in composite_convert_fields:
                        data_dict[ex['key']] = json.loads(ex['value'])
                data_dict['extras'] = [
                    ex for ex in data_dict['extras']
                    if ex['key'] not in composite_convert_fields
                ]
        else:
            dataset_composite = {
                f['field_name']
                for f in scheming_schema['dataset_fields']
                if 'repeating_subfields' in f
            }
            if dataset_composite:
                expand_form_composite(data_dict, dataset_composite)
            resource_composite = {
                f['field_name']
                for f in scheming_schema['resource_fields']
                if 'repeating_subfields' in f
            }
            if resource_composite and 'resources' in data_dict:
                for res in data_dict['resources']:
                    expand_form_composite(res, resource_composite.copy())
            # convert composite package fields to extras so they are stored
            if composite_convert_fields:
                schema = dict(
                    schema,
                    __after=schema.get('__after', []) + [composite_convert_to])

        return toolkit.navl_validate(data_dict, schema, context)


class SchemingDCATGroupsPlugin(SchemingGroupsPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)

    def about_template(self):
        return "schemingdcat/group/about.html"


class SchemingDCATOrganizationsPlugin(SchemingOrganizationsPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)

    def about_template(self):
        return "schemingdcat/organization/about.html"
