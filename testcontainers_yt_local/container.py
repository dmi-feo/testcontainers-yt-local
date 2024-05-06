from typing import Any

from yt.wrapper.client import YtClient

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class YtLocalContainer(DockerContainer):
    PORT_HTTP = 80
    PORT_RPC = 8002

    def __init__(
        self,
        image: str = "ytsaurus/local:stable",
        **kwargs: Any,
    ):
        super().__init__(image=image, **kwargs)
        self._command = [
            "--fqdn", "localhost",
           "--rpc-proxy-count", "1",
            "--rpc-proxy-port", str(YtLocalContainer.PORT_RPC),
            "--node-count", "1",
        ]
        self.with_exposed_ports(80, 8002)

    def get_client(self) -> YtClient:
        return YtClient(
            proxy=f"http://{self.get_container_host_ip()}:{self.get_exposed_port(YtLocalContainer.PORT_HTTP)}",
        )

    def get_client_rpc(self) -> YtClient:
        return YtClient(
            proxy=f"http://{self.get_container_host_ip()}:{self.get_exposed_port(YtLocalContainer.PORT_RPC)}",
            config={"backend": "rpc"},
        )

    def check_container_is_ready(self) -> None:
        assert set(self.get_client().list("/")) == {"home", "sys", "tmp", "trash"}

    @wait_container_is_ready(AssertionError)
    def _wait_container_is_ready(self) -> None:
        self.check_container_is_ready()

    def start(self) -> "YtLocalContainer":
        super().start()
        self._wait_container_is_ready()
        return self

