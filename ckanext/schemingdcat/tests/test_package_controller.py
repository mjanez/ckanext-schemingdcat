from ckanext.schemingdcat.package_controller import PackageController


def _controller():
    return PackageController()


class TestIndexLeftoverListFields:

    def test_leftover_list_moved_to_extras(self):
        data_dict = {'alternate_identifier': ['a', 'b']}
        result = _controller().index_leftover_list_fields(data_dict)

        assert 'alternate_identifier' not in result
        assert result['extras_alternate_identifier'] == 'a b'

    def test_allowlisted_theme_stays_list(self):
        data_dict = {'theme': ['t1', 't2']}
        result = _controller().index_leftover_list_fields(data_dict)

        assert result['theme'] == ['t1', 't2']
        assert 'extras_theme' not in result

    def test_tags_stays_list(self):
        data_dict = {'tags': ['alpha', 'beta']}
        result = _controller().index_leftover_list_fields(data_dict)

        assert result['tags'] == ['alpha', 'beta']
        assert 'extras_tags' not in result

    def test_stringified_leftover_moved_to_extras(self):
        data_dict = {'alternate_identifier': '["x", "y"]'}
        result = _controller().index_leftover_list_fields(data_dict)

        assert 'alternate_identifier' not in result
        assert result['extras_alternate_identifier'] == 'x y'

    def test_convert_stringified_lists_only_allowlisted(self):
        pc = _controller()
        data_dict = {
            'theme': '["t1", "t2"]',
            'alternate_identifier': '["a", "b"]',
        }
        data_dict = pc.convert_stringified_lists(data_dict)

        assert data_dict['theme'] == ['t1', 't2']
        assert data_dict['alternate_identifier'] == '["a", "b"]'
