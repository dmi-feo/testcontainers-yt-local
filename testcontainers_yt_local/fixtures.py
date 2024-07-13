import pytest

from testcontainers_yt_local.container import YtLocalContainer


def _get_yt_cluster_fixture(scope: str):
    @pytest.fixture(scope=scope)
    def the_fixture():
        with YtLocalContainer() as _yt_cluster:
            yield _yt_cluster

    return the_fixture


yt_cluster_session = _get_yt_cluster_fixture(scope="session")
yt_cluster_function = _get_yt_cluster_fixture(scope="function")
yt_cluster_module = _get_yt_cluster_fixture(scope="module")
yt_cluster_class = _get_yt_cluster_fixture(scope="class")
yt_cluster_package = _get_yt_cluster_fixture(scope="package")
