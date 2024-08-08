import pytest


pytest_plugins = ["testcontainers_yt_local"]


@pytest.fixture(scope="session", params=[False, True])
def use_ng_image(request):
    return request.param
