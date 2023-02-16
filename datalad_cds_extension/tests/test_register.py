from datalad.tests.utils_pytest import assert_result_count


def test_register():
    import datalad.api as da
    assert hasattr(da, 'download_cds')
    assert_result_count(
        da.datalad_cds_extension(),
        1,
        action='demo')

