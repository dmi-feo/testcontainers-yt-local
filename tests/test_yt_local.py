import requests

from testcontainers_yt_local.container import YtContainerInstance, YtExternalInstance


def test_docker_run_yt():
    with YtContainerInstance() as yt:
        url = f"{yt.proxy_url_http}/ping"
        r = requests.get(url)
        assert r.status_code == 200


def test_list_root_node():
    with YtContainerInstance() as yt:
        url = f"{yt.proxy_url_http}/api/v3/list"
        r = requests.get(url, params={"path": "/"})
        assert r.status_code == 200
        assert set(r.json()) == {"home", "sys", "tmp", "trash"}


def test_two_containers():
    with YtContainerInstance() as yt1, YtContainerInstance() as yt2:
        for yt in (yt1, yt2):
            url = f"{yt.proxy_url_http}/ping"
            r = requests.get(url)
            assert r.status_code == 200


def test_yt_client_config_override():
    with YtContainerInstance() as yt:
        yt_cli = yt.get_client(config={"prefix": "//tmp"})
        assert yt_cli.config["prefix"] == "//tmp"


def test_with_fixture(yt_cluster_function):
    url = f"{yt_cluster_function.proxy_url_http}/ping"
    r = requests.get(url)
    assert r.status_code == 200


def test_write_table():
    table_path = "//tmp/some_table"
    table_values = [{"some_field": "some_value"}]

    with YtContainerInstance() as yt:
        yt_cli = yt.get_client()
        yt_cli.create("table", table_path, attributes={
            "schema": [{"name": "some_field", "type": "string"}]
        })
        yt_cli.write_table(table_path, table_values)
        data = list(yt_cli.read_table(table_path))

    assert len(data) == 1
    assert data == table_values


def test_external_yt():
    with YtContainerInstance() as yt_container:
        with YtExternalInstance(proxy_url=yt_container.proxy_url_http, token="") as yt_ext:
            yt_cli_container = yt_container.get_client()
            yt_cli_ext = yt_ext.get_client()

            assert yt_cli_container.list("/") == yt_cli_ext.list("/")


def test_ng_image_ping():
    with YtContainerInstance(use_ng_image=True) as yt:
        url = f"{yt.proxy_url_http}/ping"
        r = requests.get(url)
        assert r.status_code == 200
