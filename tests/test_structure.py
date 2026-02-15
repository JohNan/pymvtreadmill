from pymvtreadmill import TreadmillClient, TreadmillUUID, TreadmillConnectionError


def test_imports() -> None:
    assert TreadmillClient is not None
    assert TreadmillUUID is not None
    assert TreadmillConnectionError is not None


def test_client_init() -> None:
    client = TreadmillClient()
    assert client._name_filter == "Mobvoi"
    assert client.speed == 0.0
    assert client.inclination is None
    assert client.distance is None
    assert not client.is_running
