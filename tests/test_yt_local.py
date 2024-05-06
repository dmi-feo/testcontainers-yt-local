import requests

from testcontainers_yt_local.container import YtLocalContainer


def test_docker_run_yt():
    yt_container = YtLocalContainer()
    with yt_container as yt:
        url = f"http://{yt.get_container_host_ip()}:{yt.get_exposed_port(YtLocalContainer.PORT_HTTP)}/ping"
        r = requests.get(url)
        assert r.status_code == 200


def test_list_root_node():
    with YtLocalContainer() as yt:
        url = f"http://{yt.get_container_host_ip()}:{yt.get_exposed_port(YtLocalContainer.PORT_HTTP)}/api/v3/list"
        r = requests.get(url, params={"path": "/"})
        assert r.status_code == 200
        assert set(r.json()) == {"home", "sys", "tmp", "trash"}


def test_two_containers():
    with YtLocalContainer() as yt1, YtLocalContainer() as yt2:
        for yt in (yt1, yt2):
            url = f"http://{yt.get_container_host_ip()}:{yt.get_exposed_port(YtLocalContainer.PORT_HTTP)}/ping"
            r = requests.get(url)
            assert r.status_code == 200
