# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.2.3...HEAD)</small>

<!-- insertion marker -->
## [v3.2.3](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.2.3) - 2024-10-22

- Add snippets needed by ckanext-iepnb ([422f1ef](https://github.com/mjanez/ckanext-schemingdcat/commit/422f1ef754eb8c4fc231dcda847d02e4831921f4) by mjanez).

<small>[Compare with v3.2.2](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.2.2...v3.2.3)</small>

### Fixed

- Fix dataset_id_field assignment in XLS harvester configuration ([bfe0597](https://github.com/mjanez/ckanext-schemingdcat/commit/bfe0597b289e366fb054864f34e4f1d31b7c8495) by mjanez).

## [v3.2.2](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.2.2) - 2024-09-10

<small>[Compare with v3.2.1](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.2.1...v3.2.2)</small>

### Added

- Add allow_private_datasets to ckan harvester ([9e5037a](https://github.com/mjanez/ckanext-schemingdcat/commit/9e5037a53591c4cfe4b2ae7f073d68f11a4ec93a) by mjanez).
- Add schemingdcat_get_choice_property helper ([b4ec09e](https://github.com/mjanez/ckanext-schemingdcat/commit/b4ec09e5f4cdf667e3175b93b8d6e162db308b26) by mjanez).

### Fixed

- Fix before_update ([c347255](https://github.com/mjanez/ckanext-schemingdcat/commit/c347255f3eeb94c8c9f29e7dfaaa8736c2de04d1) by mjanez).
- Fixed bugs with localised_filesize snippet ([43cc8b0](https://github.com/mjanez/ckanext-schemingdcat/commit/43cc8b025e6e7574dad952b1a6b680a4a66dbcff) by mjanez).
- Fix CKAN harvester search functionality ([3952322](https://github.com/mjanez/ckanext-schemingdcat/commit/3952322c036b7eeb4d3b2407448c943a842cf521) by mjanez).
- Fix file_size in resource metadata info ([32d7901](https://github.com/mjanez/ckanext-schemingdcat/commit/32d790181001f92036183cf1607f865c4d9c5ce5) by mjanez).
- Fix bug when schemingdcat.endpoints_yaml is None ([36a298e](https://github.com/mjanez/ckanext-schemingdcat/commit/36a298e9b3f2671c477dbf02da6280d61284aa07) by mjanez).
- Fix schemas README link ([bee583e](https://github.com/mjanez/ckanext-schemingdcat/commit/bee583e0ead01b31f9be3cfb79631283869a722f) by mjanez).
- Fix search box width ([2abe18e](https://github.com/mjanez/ckanext-schemingdcat/commit/2abe18e0ac73c376ad2aab777e961d7e5a5b4365) by mjanez).
- Fix search box in datasets/orgs/groups ([a5a58e2](https://github.com/mjanez/ckanext-schemingdcat/commit/a5a58e2448886343be8ebf0f54fdee66b3d61f95) by mjanez).

## [v3.2.1](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.2.1) - 2024-07-10

<small>[Compare with v3.2.1-alpha](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.2.1-alpha...v3.2.1)</small>

### Fixed

- Fix problem with defaults_values from config ([ea02b53](https://github.com/mjanez/ckanext-schemingdcat/commit/ea02b530dc2cc48eae9620204a7eec14184114b5) by mjanez).
- Fix resource mimetype update ([3217e8d](https://github.com/mjanez/ckanext-schemingdcat/commit/3217e8d9db5cff46d930a229e93db17fa18c88dd) by mjanez).

## [v3.2.1-alpha](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.2.1-alpha) - 2024-06-27

<small>[Compare with first commit](https://github.com/mjanez/ckanext-schemingdcat/compare/a64993ad67b965a189677806b3f3588ed7b20fc1...v3.2.1-alpha)</small>

### Added

- Add admin/config template i18n ([c58f697](https://github.com/mjanez/ckanext-schemingdcat/commit/c58f697f4d998cd23356f6305f8cf3e8deb6aa30) by mjanez).
- Add schemingdcat_xls harvester template ([3b118b2](https://github.com/mjanez/ckanext-schemingdcat/commit/3b118b2624805962cd847fcb0af842adc9a3df20) by mjanez).
- Add info to schemingdcat_ows harvester ([e19957c](https://github.com/mjanez/ckanext-schemingdcat/commit/e19957c8596541ee14454ca41eac157c832bc3d6) by mjanez).

### Fixed

- Fix endpoints template when sparql_interface is not active ([a608ad2](https://github.com/mjanez/ckanext-schemingdcat/commit/a608ad28a40beea622b3fe025fe7fba4e8f73735) by mjanez).
- Fix translation issue in schemingdcat_facet_list template ([9e91862](https://github.com/mjanez/ckanext-schemingdcat/commit/9e918622d6ff91d29532bfe8f2fe783007b52f1c) by mjanez).

## [v3.2.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.2.0) - 2024-06-17

<small>[Compare with v3.1.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.1.0...v3.2.0)</small>

### Added

- Adding metadata template logic and theming ([1acfab4](https://github.com/mjanez/ckanext-schemingdcat/commit/1acfab4a02e91be62bc11cfb3b3b5e884e72e618) by mjanez).
- Add metatata templates sidebar for schemingdcat_xls harvester ([f01c058](https://github.com/mjanez/ckanext-schemingdcat/commit/f01c058843f864304e437ad690ba3e836ea248ee) by mjanez).
- Add display snippet for spatial JSON in default presets ([cb8da30](https://github.com/mjanez/ckanext-schemingdcat/commit/cb8da30ec8aa87250e9880dc7d52dd15775064e6) by mjanez).
- Add custom format validator ([7ec5510](https://github.com/mjanez/ckanext-schemingdcat/commit/7ec5510ae375ea8db4bc032f9ae88d604cb1546d) by mjanez).
- Add EU to spatial_uri ([e92c96c](https://github.com/mjanez/ckanext-schemingdcat/commit/e92c96cd76270dfd86aa7e14995f3fbf0e410692) by mjanez).
- Add css for distribution formats ([b16bece](https://github.com/mjanez/ckanext-schemingdcat/commit/b16becee7f56aba6e24738e5e2b76bcfa0880b77) by mjanez).
- Add temporal_start and temporal_end fields to DATE_FIELDS ([f37bb45](https://github.com/mjanez/ckanext-schemingdcat/commit/f37bb45dcf7988021bb3e84511b7ca211c98480e) by mjanez).
- Add data-icons for provincias and provincias images based on autonomies ([7ce296d](https://github.com/mjanez/ckanext-schemingdcat/commit/7ce296df13bb4df6c3a481c755348569f5120a6c) by mjanez).
- Add schemingdcat_spatial_uri_validator to obtain spatial from spatial_uri ([522415c](https://github.com/mjanez/ckanext-schemingdcat/commit/522415c364a955581289069ad5410bf2618f127f) by mjanez).

### Fixed

- Fix list elements ([91189db](https://github.com/mjanez/ckanext-schemingdcat/commit/91189dbc95cb24ec6665dd7e21eb529e5a19416c) by mjanez).
- Fix ZIP format color ([056e3a4](https://github.com/mjanez/ckanext-schemingdcat/commit/056e3a4076efa22b25f73fe9773a3d622c46837d) by mjanez).
- Fix local_schema in import_stage ([c62daba](https://github.com/mjanez/ckanext-schemingdcat/commit/c62daba4912523996a51105401e1cc235fd8ec19) by mjanez).
- Fix spaces between warnings in metadata-templates ([9dde146](https://github.com/mjanez/ckanext-schemingdcat/commit/9dde146d9ab6f6571baea89b5475dbd3f85f0512) by mjanez).
- Fix contact/publisher info snippets to avoid errors with emails ([5271ed9](https://github.com/mjanez/ckanext-schemingdcat/commit/5271ed9ec6c6eed85124c6c70ba1d50531f10d69) by mjanez).
- Fix icon class for university publisher type ([30b3e35](https://github.com/mjanez/ckanext-schemingdcat/commit/30b3e35eca48f52c824b0034b54a49982a7d7eda) by mjanez).
- Fix contact_info and publisher_info snippets ([661b431](https://github.com/mjanez/ckanext-schemingdcat/commit/661b4316e70052cf9e7fce71300f3ad3d901a052) by mjanez).
- Fix stages css ([3d2069a](https://github.com/mjanez/ckanext-schemingdcat/commit/3d2069a3328e8f9a95acbc846975332da8e67fac) by mjanez).
- Fix schemingdcat_prettify_url_name ([288f75f](https://github.com/mjanez/ckanext-schemingdcat/commit/288f75f206b02e3e0acdbbb7349f1c42462d31df) by mjanez).
- Fix org form_placeholder ([d4ff46c](https://github.com/mjanez/ckanext-schemingdcat/commit/d4ff46cc2e6005b1c4446b177e92c1b6f5fc9e78) by mjanez).
- Fix badges ([490e65f](https://github.com/mjanez/ckanext-schemingdcat/commit/490e65f496b389b95bb470f1e003cf85e9a78250) by mjanez).
- Fix flags from spatial_uri in contac_info snippet ([c2c9bcd](https://github.com/mjanez/ckanext-schemingdcat/commit/c2c9bcd6b03bae5b3e7616e8fe816cfd5a62a9f6) by mjanez).
- Fix dataset-categories icons position ([0b81573](https://github.com/mjanez/ckanext-schemingdcat/commit/0b8157358e0ae90c8e736af1d3e6d64b5827fa27) by mjanez).

### Removed

- Remove logs ([f9fbccd](https://github.com/mjanez/ckanext-schemingdcat/commit/f9fbccdc64b1e206e6350df9d405064e553c8eed) by mjanez).

## [v3.1.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.1.0) - 2024-05-28

<small>[Compare with v3.0.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v3.0.0...v3.1.0)</small>

### Added

- Add icons to package items to render theme/spatial_uri ([fcd7bbe](https://github.com/mjanez/ckanext-schemingdcat/commit/fcd7bbe09b2eacf7bee4dbec922a2793cc7c5d4c) by mjanez).
- Add non_spatial_dataset field ([b455bc6](https://github.com/mjanez/ckanext-schemingdcat/commit/b455bc6386e655ec0b7a53e99995607b47443536) by mjanez).
- Add endpoint index to endpoints layout ([2beff9d](https://github.com/mjanez/ckanext-schemingdcat/commit/2beff9df99778ed80edf285de5d07f66d85a2ffd) by mjanez).
- Add /endpoints blueprint ([ebba116](https://github.com/mjanez/ckanext-schemingdcat/commit/ebba116b0021c5b5987ec07982c812f755bf1e98) by mjanez).
- Add get_ckan_cleaned_name helper ([133a40c](https://github.com/mjanez/ckanext-schemingdcat/commit/133a40c156179db17896f5372c0ebc07ddb5b0e3) by mjanez).
- Add theme_es, theme, theme_eu, topic and hvd_category to translations ([a76873e](https://github.com/mjanez/ckanext-schemingdcat/commit/a76873e129bb7661f96fe07cf58938ec025ed6c1) by mjanez).
- Add commands to create tags based on schema themes and topics ([0f75976](https://github.com/mjanez/ckanext-schemingdcat/commit/0f7597638e91e5d1599e6b79c2cc4d953f188cc4) by mjanez).
- Add multiple_choice_custom_tag preset ([050d157](https://github.com/mjanez/ckanext-schemingdcat/commit/050d157c39a350ce24863570ebe119841c4f13f9) by mjanez).
- Add YAML file and script for generating translation files ([01fc225](https://github.com/mjanez/ckanext-schemingdcat/commit/01fc225f3953602aa025859a739057e81f04edee) by mjanez).
- Add debug info to header in dev mode ([a053b43](https://github.com/mjanez/ckanext-schemingdcat/commit/a053b43f70bb684241a94ca325a15b1100fab3b2) by mjanez).
- Add hvd_category to metadata_info template ([e79209a](https://github.com/mjanez/ckanext-schemingdcat/commit/e79209a60b7c991cfe67969af0c8ce9418fe698e) by mjanez).
- Add select_spatial_icon preset for geographic identifier field ([332ceec](https://github.com/mjanez/ckanext-schemingdcat/commit/332ceec0db82859357995e5c4dce8dc1f1135bb7) by mjanez).
- Add high-value dataset category field ([cf42f5b](https://github.com/mjanez/ckanext-schemingdcat/commit/cf42f5bba6863432697222f6ab96e3a1f194252a) by mjanez).

### Fixed

- Fix theme_es classes ([083e500](https://github.com/mjanez/ckanext-schemingdcat/commit/083e50078ffa5d1dd25421d2e7a8d8e25a975153) by mjanez).
- FIx generate_translation_files ([cb1ff4d](https://github.com/mjanez/ckanext-schemingdcat/commit/cb1ff4df293719593d83b0718ad08b1f48f91199) by mjanez).

## [v3.0.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v3.0.0) - 2024-04-27

<small>[Compare with v2.1.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v2.1.0...v3.0.0)</small>

### Fixed

- Fix ckan harvester issues ([93da11a](https://github.com/mjanez/ckanext-schemingdcat/commit/93da11a97b3a5ed55c586a63ad76a8986d47b1a7) by mjanez).
- Fix resource/dataset update when use XLS Harvester ([b1117c0](https://github.com/mjanez/ckanext-schemingdcat/commit/b1117c0d110deca3ff8de1ec042245d024e17106) by mjanez).
- Fix accented character handling in SchemingDCATHarvester ([9074fed](https://github.com/mjanez/ckanext-schemingdcat/commit/9074fed29aa1bfacbb57404460cc0a840947c081) by mjanez).
- Fix source_date_format issue in SchemingDCATHarvester ([0fca9da](https://github.com/mjanez/ckanext-schemingdcat/commit/0fca9da26533ec204dfa5c8800cc259fbc7ff01b) by mjanez).
- Fix resource updating for XLS harvester ([35e1371](https://github.com/mjanez/ckanext-schemingdcat/commit/35e137196c46eed44a4287f84415066b3148b3c6) by mjanez).
- Fix old scheming_dcat prefix and adapt helpers from harvest ([54b9833](https://github.com/mjanez/ckanext-schemingdcat/commit/54b9833a91c1944b3994d397a0b7fc385dfca682) by mjanez).
- Fix bugs ckan harvester ([b309e1a](https://github.com/mjanez/ckanext-schemingdcat/commit/b309e1ab776af5f4591642b5d28d4aaf87ebb802) by mjanez).
- Fix extras instance in SchemingDCATHarvester ([560863c](https://github.com/mjanez/ckanext-schemingdcat/commit/560863cd68614871bab83d4bc88b27f8cb75a13f) by mjanez).
- Fix map attribution acording to ckanext-spatial ([b8782c6](https://github.com/mjanez/ckanext-schemingdcat/commit/b8782c60eb1110efdeee33c0e77b6e8eb506c95c) by mjanez).
- Fix all to schemingdcat ([1cf8bfb](https://github.com/mjanez/ckanext-schemingdcat/commit/1cf8bfbb7ac91e0ab012fad4f73f8aca833b68c8) by mnjnz).
- Fix scheming_dcat name to schemingdcat (PEP 503 y PEP 508) ([7f30286](https://github.com/mjanez/ckanext-schemingdcat/commit/7f30286d8b26bbe8c5ba675725823a6eaaffa261) by mjanez).

### Removed

- Remove duplicate LICENSE.txt ([e6d2c22](https://github.com/mjanez/ckanext-schemingdcat/commit/e6d2c22a8a97ebbbeb58334bb829b33b815789fe) by mjanez).
- Remove log.debug ([6f49461](https://github.com/mjanez/ckanext-schemingdcat/commit/6f494612eb211d9431c682787e6a45021ac9bc9a) by mjanez).

## [v2.1.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v2.1.0) - 2024-03-11

<small>[Compare with v2.0.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v2.0.0...v2.1.0)</small>

### Added

- Add default values to package_dict ([ed746d1](https://github.com/mjanez/ckanext-schemingdcat/commit/ed746d121ad680a758c21d42c95aafdf57d0ef8c) by mjanez).
- Add gspread auth storage_type ([b7c3957](https://github.com/mjanez/ckanext-schemingdcat/commit/b7c3957db9530a2f14502b81bfcf7463b8b0e127) by mjanez).
- Add new XLS Harvester ([81f32ad](https://github.com/mjanez/ckanext-schemingdcat/commit/81f32adfbc3487b8a2582d456a8b9fe5f28144f2) by mjanez).
- Add scheming_dcat harvester plugins ([42bfafc](https://github.com/mjanez/ckanext-schemingdcat/commit/42bfafc2df10286a3dc6d12d8a1d8ad55545db4e) by mjanez).

### Fixed

- Fix groups ingest ([9f5c6c3](https://github.com/mjanez/ckanext-schemingdcat/commit/9f5c6c375338e32d13dd7d529584e0a2a03c21b1) by mjanez).
- Fix codelists folder ([128aa5c](https://github.com/mjanez/ckanext-schemingdcat/commit/128aa5c413207b152677671f04eb97b7cb9691ed) by mjanez).
- Fix csw harvester WIP ([095acfe](https://github.com/mjanez/ckanext-schemingdcat/commit/095acfe58c8a9352accc8ea556f55b7dbe296b79) by mjanez).
- Fix group items templates in dataset ([eddee38](https://github.com/mjanez/ckanext-schemingdcat/commit/eddee380c9749cf2ff252f3e029af1c0dbe88bdf) by mjanez).

## [v2.0.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v2.0.0) - 2023-10-20

<small>[Compare with v1.2.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v1.2.0...v2.0.0)</small>

### Added

- Add multilang to groups and organisations ([c046561](https://github.com/mjanez/ckanext-schemingdcat/commit/c046561259213ce9e91b0ed2615e1d29ef3aeb44) by mjanez).
- Add multilang to search templates ([5ab6bfd](https://github.com/mjanez/ckanext-schemingdcat/commit/5ab6bfd7b0a3d5df3bb9cc92fbd83a8e6dc2370d) by mjanez).
- Add multilang promoted home text (intro_text) ([3ebec32](https://github.com/mjanez/ckanext-schemingdcat/commit/3ebec32a74679541c822c97c14e37e869f57cf47) by mjanez).
- Add modern theme to CKAN and CSW/LOD endpoints at home ([26114c1](https://github.com/mjanez/ckanext-schemingdcat/commit/26114c1912a92b5e1a7ed24e846e75d85b6c4041) by mjanez).

### Fixed

- Fix scheming_dct_get_localised_value_from_dict to allow use of untranslated field ([253c637](https://github.com/mjanez/ckanext-schemingdcat/commit/253c6373d74096e23a871d0c17668ba121ce7280) by mjanez).
- Fix default lang, prefer schema required and then locale_default ([45fd50b](https://github.com/mjanez/ckanext-schemingdcat/commit/45fd50b5ef47e171ca5720186aa830ac2216af32) by mjanez).
- Fix multilang display and core fields validator ([e03c38c](https://github.com/mjanez/ckanext-schemingdcat/commit/e03c38cc5161bb8b2763bc1ce75085f855a935d8) by mjanez).
- Fix ckanext-fluent with custom extensions ([0b6e9b8](https://github.com/mjanez/ckanext-schemingdcat/commit/0b6e9b8d088cab604a9fe80e11d6ab2751f36300) by mjanez).
- Fix schemingdct_prettify_url_name ([3894ded](https://github.com/mjanez/ckanext-schemingdcat/commit/3894ded883d62c05de4c5e10615dbf5e8b727f38) by mjanez).
- Fix schemingdct_prettify_url_name to avoid Nones ([2353f61](https://github.com/mjanez/ckanext-schemingdcat/commit/2353f616a898a04817bd46b9ac0c6c5dc599632d) by mjanez).
- Fix header logo and footer ([6e13958](https://github.com/mjanez/ckanext-schemingdcat/commit/6e13958759132fc7cc377896f01363b9ee859782) by mjanez).
- Fix sd_config.endpoints ([3f8a89f](https://github.com/mjanez/ckanext-schemingdcat/commit/3f8a89f88938710c71db54a297d44e7ca6c3dce4) by mjanez).

## [v1.2.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v1.2.0) - 2023-09-06

<small>[Compare with v1.1.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v1.1.0...v1.2.0)</small>

### Added

- add purpose metadata element to GeoDCAT-AP Schemas ([d283a14](https://github.com/mjanez/ckanext-schemingdcat/commit/d283a143c1140968bbb85567c28692fc48d337d5) by mjanez).
- Add new packages read templates ([f77250b](https://github.com/mjanez/ckanext-schemingdcat/commit/f77250baf9385c28a408bff3a915a159f6fe7175) by mjanez).
- Add Js assets ([2537057](https://github.com/mjanez/ckanext-schemingdcat/commit/25370571cf177f16d14fda64b1cca0e5ce26f495) by mjanez).
- Add theme_es to schemingdct_info if exists ([d05afc9](https://github.com/mjanez/ckanext-schemingdcat/commit/d05afc95e1fa8117dcaeb9ce0d70719ddbc8189a) by mjanez).
- Add spatial_uri for EU Context ([dac2a14](https://github.com/mjanez/ckanext-schemingdcat/commit/dac2a14f22452d8dfb2d10c9f95a76a92424ba75) by mjanez).
- Add schemas info to README ([6b13b61](https://github.com/mjanez/ckanext-schemingdcat/commit/6b13b618fb2b70b7f05f575abecbf13dc48c31ff) by mjanez).
- Add dcat base schema ([9a9e648](https://github.com/mjanez/ckanext-schemingdcat/commit/9a9e6485ba2457168209cd771e0c43165c57666e) by mjanez).

### Fixed

- Fix yaml error ([38ecc47](https://github.com/mjanez/ckanext-schemingdcat/commit/38ecc47c7cecb8fc17d7ed8bdd4f67cdac0c92f2) by mjanez).
- Fix resourcedictionary in package_resource template ([51540f2](https://github.com/mjanez/ckanext-schemingdcat/commit/51540f26a60dee4f3615297da1c619ee5e3a8763) by mjanez).
- Fix org bulk_process template ([035bca6](https://github.com/mjanez/ckanext-schemingdcat/commit/035bca65d32a4f9a49fc557d70f7d19976d0dadb) by mjanez).
- Fix snippets ([4292ee1](https://github.com/mjanez/ckanext-schemingdcat/commit/4292ee14f7bcc8dd8eecb7b8ccde8bc154467c07) by mjanez).
- Fix custom_data snippets ([a2e900c](https://github.com/mjanez/ckanext-schemingdcat/commit/a2e900cc741eb864ab2e34ed89e0b5614cfb6596) by mjanez).
- Fix resource_read with extra fields ([be8b038](https://github.com/mjanez/ckanext-schemingdcat/commit/be8b0387aafe4d6a4b0707600657b955226c50d0) by mjanez).
- Fix info snippet from package ([d9458bc](https://github.com/mjanez/ckanext-schemingdcat/commit/d9458bc577a14bdf573134cae12fb0afa751f4c4) by mjanez).
- Fix resource_read ([b0efb43](https://github.com/mjanez/ckanext-schemingdcat/commit/b0efb4379cbbfadd94f7dbeb432c9babf87aa6f2) by mjanez).
- Fix data_access_license block ([d06a864](https://github.com/mjanez/ckanext-schemingdcat/commit/d06a8647c317de3981619666031f8cd4d15b0243) by mjanez).
- Fix read_base secondary items ([948a180](https://github.com/mjanez/ckanext-schemingdcat/commit/948a1803393882acc4057e59140a099e0f35df5c) by mjanez).
- Fix ckan helper deprecated ([dd17e48](https://github.com/mjanez/ckanext-schemingdcat/commit/dd17e482d8c98dfffe170f0d16ab40398b015922) by mjanez).
- Fix data_access_license if not access_rights ([87274bf](https://github.com/mjanez/ckanext-schemingdcat/commit/87274bf83cf616623239aa90f50ab7854ac8a9c3) by mjanez).
- Fix image org css (schemingdct_info) ([8d0840a](https://github.com/mjanez/ckanext-schemingdcat/commit/8d0840acb4251477694fb4c323ea79e3e1c63969) by mjanez).
- Fix data_access_license template ([7730310](https://github.com/mjanez/ckanext-schemingdcat/commit/7730310cdcfdafacc708f6d581f805d35ade4447) by mjanez).
- Fix translation ([0cca67f](https://github.com/mjanez/ckanext-schemingdcat/commit/0cca67f712f9138499626d9348458f6f073098c5) by mjanez).
- Fix spatial_query translates ([38724ce](https://github.com/mjanez/ckanext-schemingdcat/commit/38724cee26dfdb264c3b99b766523bd9cd5cad20) by mjanez).
- Fix setup/plugin.py ([8945eab](https://github.com/mjanez/ckanext-schemingdcat/commit/8945eabdaf9903902a7e2fd6558d243f3f1d7e51) by mjanez).
- Fix README ([103d5d5](https://github.com/mjanez/ckanext-schemingdcat/commit/103d5d5adca8a067c80fc1679f847553718d4a29) by mjanez).
- Fix GeoDCAT-AP Schema and add geodcatap_es base ([26252ea](https://github.com/mjanez/ckanext-schemingdcat/commit/26252eaf4182fc7f19ffdde73330d1befebd5aa7) by mjanez).

### Removed

- Remove debug in table-collapsible-rows module ([7807771](https://github.com/mjanez/ckanext-schemingdcat/commit/7807771021bfc7f9bee790999cb0baf1c42350d5) by mjanez).

## [v1.1.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v1.1.0) - 2023-08-22

<small>[Compare with v1.0.0](https://github.com/mjanez/ckanext-schemingdcat/compare/v1.0.0...v1.1.0)</small>

### Fixed

- Fix package/read_base.html ([c8f02aa](https://github.com/mjanez/ckanext-schemingdcat/commit/c8f02aa0207973f73fd9b9a9c996de30e4eedae8) by mjanez).
- Fix geodcatap schema ([a61ceca](https://github.com/mjanez/ckanext-schemingdcat/commit/a61ceca0fba3fa9503343b921cebbdc10187db88) by mjanez).
- Fix py files ([c00a8e4](https://github.com/mjanez/ckanext-schemingdcat/commit/c00a8e4e1ac7890388b89e816dedeb8d2e75f855) by mjanez).

## [v1.0.0](https://github.com/mjanez/ckanext-schemingdcat/releases/tag/v1.0.0) - 2023-08-16

<small>[Compare with first commit](https://github.com/mjanez/ckanext-schemingdcat/compare/7e4fd3eb2b8d07aa536e1d66698a2db21b85859b...v1.0.0)</small>

### Fixed

- Fix spatial_uri hrefs & icon render ([9d7867c](https://github.com/mjanez/ckanext-schemingdcat/commit/9d7867ce8693e3250a3882bffebe67d1a17fc2e7) by mjanez).
- Fix doc ([9dd6d7f](https://github.com/mjanez/ckanext-schemingdcat/commit/9dd6d7f0f313ba2b89c8a120d4fc2174ece96e3e) by mjanez).
- Fix filenames ([c863c7e](https://github.com/mjanez/ckanext-schemingdcat/commit/c863c7ef9283c1e678dbb48ad71ac0f4d681bf2a) by mjanez).
- Fix README ([775a2ce](https://github.com/mjanez/ckanext-schemingdcat/commit/775a2ce42243c4fb718224dfe04870b28a98496f) by mjanez).
- Fix setup and i18n ([efa5b75](https://github.com/mjanez/ckanext-schemingdcat/commit/efa5b75df0f89da91522a8dc03366212145e154f) by mjanez).
- Fix geodcatap schema ([42d64af](https://github.com/mjanez/ckanext-schemingdcat/commit/42d64af7937ec4a3923c7b72b1075d62bfaf360f) by mjanez).
- Fix .gitignore files ([6d773c0](https://github.com/mjanez/ckanext-schemingdcat/commit/6d773c08ce8d67efbf085999415b808f86bd090e) by mjanez).
- Fix errors ([d768ce1](https://github.com/mjanez/ckanext-schemingdcat/commit/d768ce1431d6a75a103714bfa82d90cc037cbe0e) by mnjnz).
- Fix setup.py to facet_scheming ([8dc719c](https://github.com/mjanez/ckanext-schemingdcat/commit/8dc719c1e49e11f76ab63ca0401204b04c826331) by mnjnz).
- Fix 2 ([6be368a](https://github.com/mjanez/ckanext-schemingdcat/commit/6be368a7004c5d58a5ab12d5025d8409a2451977) by mnjnz).
- Fix #1 ([1dfd51e](https://github.com/mjanez/ckanext-schemingdcat/commit/1dfd51efc125ada1464e3eed86f5f1f24b379062) by mnjnz).
- Fix extension name & update README ([cf855ad](https://github.com/mjanez/ckanext-schemingdcat/commit/cf855adceb8691163e82c6938ba656330db5ae44) by mjanez).

