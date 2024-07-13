import requests

from testcontainers_yt_local.container import YtLocalContainer


def test_docker_run_yt():
    with YtLocalContainer() as yt:
        url = f"{yt.proxy_url_http}/ping"
        r = requests.get(url)
        assert r.status_code == 200


def test_list_root_node():
    with YtLocalContainer() as yt:
        url = f"{yt.proxy_url_http}/api/v3/list"
        r = requests.get(url, params={"path": "/"})
        assert r.status_code == 200
        assert set(r.json()) == {"home", "sys", "tmp", "trash"}


def test_two_containers():
    with YtLocalContainer() as yt1, YtLocalContainer() as yt2:
        for yt in (yt1, yt2):
            url = f"{yt.proxy_url_http}/ping"
            r = requests.get(url)
            assert r.status_code == 200


def test_yt_client_config_override():
    with YtLocalContainer() as yt:
        yt_cli = yt.get_client(config={"prefix": "//tmp"})
        assert yt_cli.config["prefix"] == "//tmp"


def test_with_fixture(yt_cluster_function):
    url = f"{yt_cluster_function.proxy_url_http}/ping"
    r = requests.get(url)
    assert r.status_code == 200
