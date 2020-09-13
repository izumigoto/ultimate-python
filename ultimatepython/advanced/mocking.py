from collections import Counter
from unittest.mock import MagicMock, PropertyMock, patch

# Module-level constants
_COUNTER = Counter(pid=1)
_START_SUCCESS = "success"
_START_FAILURE = "failure"
_PROTOCOL_HTTP = "http"
_PROTOCOL_HTTPS = "https"
_FAKE_BASE_URL = f"{_PROTOCOL_HTTPS}://www.google.com:443"
_FAKE_PID = 127


class AppServer:
    """Application server.

    Normally we don't mock an application server because it is the runtime
    environment (AKA central nervous system) for business logic, database
    endpoints, network sockets and more. However, this server definition
    is lightweight, so it's acceptable to mock this.
    """

    def __init__(self, host, port, proto):
        self._host = host
        self._port = port
        self._proto = proto
        self._pid = -1

    @property
    def endpoint(self):
        return f"{self._proto}://{self._host}:{self._port}"

    @property
    def pid(self):
        return self._pid

    @property
    def started(self):
        return self.pid > 0

    def start_server(self):
        if self.started:
            return _START_FAILURE
        self._pid = _COUNTER["pid"]
        _COUNTER["pid"] += 1
        return _START_SUCCESS


class FakeServer(AppServer):
    """Subclass parent and fake some routines."""

    @property
    def endpoint(self):
        """Mock output of public URL."""
        return _FAKE_BASE_URL

    @property
    def pid(self):
        """Mock output of public PID."""
        return _FAKE_PID


def main():
    # This is the original class and it works as expected
    app_server = AppServer("localhost", 8000, _PROTOCOL_HTTP)
    assert app_server.endpoint == "http://localhost:8000"
    assert app_server.start_server() == _START_SUCCESS
    assert app_server.started is True
    assert app_server.start_server() == _START_FAILURE

    # But sometimes you cannot test the finer details of a class because
    # its methods depend on the availability of external resources. This
    # is where mocking comes to the rescue. There are a couple approaches
    # that developers use when it comes to mocking

    # Approach 1: Use a `MagicMock` in place of a real class instance
    mock_server = MagicMock()
    assert isinstance(mock_server, MagicMock)
    assert isinstance(mock_server.start_server(), MagicMock)
    mock_server.start_server.assert_called()
    mock_server.endpoint.assert_not_called()

    # Approach 2: Patch a method in the original class
    with patch.object(AppServer, "endpoint", PropertyMock(return_value=_FAKE_BASE_URL)):
        patch_server = AppServer("localhost", 8080, _PROTOCOL_HTTP)
        assert isinstance(patch_server, AppServer)
        assert patch_server.endpoint == _FAKE_BASE_URL
        assert patch_server.started is False
        assert patch_server.start_server() == _START_SUCCESS

    # Approach 3: Create a new class that inherits the original class
    fake_server = FakeServer("localhost", 8080, _PROTOCOL_HTTP)
    assert isinstance(fake_server, AppServer)
    assert fake_server.endpoint == _FAKE_BASE_URL
    assert fake_server.started is True
    assert patch_server.start_server() == _START_FAILURE


if __name__ == "__main__":
    main()