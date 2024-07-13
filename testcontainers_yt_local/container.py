import abc
from typing import Any, Optional, Dict

from yt.wrapper.client import YtClient
from deepmerge import always_merger
from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


DEFAULT_CLIENT_CONFIG = {
    "proxy": {
        "enable_proxy_discovery": False,
    }
}


class YtBaseInstance(abc.ABC):
    @abc.abstractmethod
    def __enter__(self) -> Self:
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @property
    @abc.abstractmethod
    def proxy_url_http(self) -> str:
        pass

    @abc.abstractmethod
    def get_client(self, config: Optional[Dict[str, Any]] = None) -> YtClient:
        pass


class YtContainerInstance(DockerContainer, YtBaseInstance):
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
            "--rpc-proxy-port", str(self.PORT_RPC),
            "--node-count", "1",
        ]
        self.with_exposed_ports(80, 8002)

    @property
    def proxy_url_http(self):
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.PORT_HTTP)}"

    @property
    def proxy_url_rpc(self):
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.PORT_RPC)}"

    def get_client(self, config: Optional[Dict[str, Any]] = None) -> YtClient:
        effective_config = always_merger.merge(DEFAULT_CLIENT_CONFIG, config or {})
        return YtClient(
            proxy=self.proxy_url_http,
            config=effective_config,
        )

    def get_client_rpc(self, config: Optional[Dict[str, Any]] = None) -> YtClient:
        effective_config = always_merger.merge(DEFAULT_CLIENT_CONFIG, config or {})
        return YtClient(
            proxy=self.proxy_url_rpc,
            config={**effective_config, "backend": "rpc"},
        )

    def check_container_is_ready(self) -> None:
        assert set(self.get_client().list("/")) == {"home", "sys", "tmp", "trash"}

    @wait_container_is_ready(AssertionError)
    def _wait_container_is_ready(self) -> None:
        self.check_container_is_ready()

    def start(self) -> Self:
        super().start()
        self._wait_container_is_ready()
        return self


YtLocalContainer = YtContainerInstance  # for backward compatibility


class YtExternalInstance(YtBaseInstance):
    def __init__(self, proxy_url: str, token: str):
        self.proxy_url = proxy_url
        self.token = token

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @property
    def proxy_url_http(self) -> str:
        return self.proxy_url

    def get_client(self, config: Optional[Dict[str, Any]] = None) -> YtClient:
        return YtClient(
            proxy=self.proxy_url_http,
            config=config,
        )
