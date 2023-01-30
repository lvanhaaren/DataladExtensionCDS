from datalad.tests.utils_pytest import assert_result_count


def test_register():
    import datalad.api as da
    assert hasattr(da, 'datalad_cds_extension')
    assert_result_count(
        da.datalad_cds(),
        1,
        action='demo')

