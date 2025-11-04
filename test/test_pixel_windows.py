import pytest
import requests
from urllib.error import URLError


def test_pixwin_download(monkeypatch):
    """Test that pixwin downloads and caches the file using astropy if not present locally."""
    import healpy as hp

    nside = 32
    # Remove any local file by monkeypatching os.path.isfile to always return False
    monkeypatch.setattr("os.path.isfile", lambda path: False)
    pw = hp.pixwin(nside)
    assert pw is not None
    assert len(pw) == 3 * nside - 1 + 1


def test_pixwin_local_datapath(tmp_path):
    """Test that pixwin loads the file from a local datapath if provided."""
    import healpy as hp

    nside = 32
    datapath = tmp_path / "pixel_window_functions"
    datapath.mkdir(parents=True)
    # Download the file from healpy-data repo
    url = (
        "https://github.com/healpy/healpy-data/"
        "raw/master/pixel_window_functions/"
        f"pixel_window_n{nside:04d}.fits"
    )
    r = requests.get(url)
    local_file = datapath / f"pixel_window_n{nside:04d}.fits"
    with open(local_file, "wb") as f:
        f.write(r.content)
    pw = hp.pixwin(nside, datapath=tmp_path)
    assert pw is not None
    assert len(pw) == 3 * nside - 1 + 1


def test_pixwin_missing_local_file(tmp_path):
    """Ensure specifying datapath without the pixel window file fails fast."""
    import healpy as hp

    nside = 32
    datapath = tmp_path / "pixel_window_functions"
    datapath.mkdir(parents=True)
    with pytest.raises(ValueError, match="Pixel window file not found"):
        hp.pixwin(nside, datapath=tmp_path)


def test_pixwin_remote_missing_file(monkeypatch):
    """Ensure remote download errors bubble up as informative ValueErrors."""
    import healpy as hp

    def raise_url_error(*args, **kwargs):
        raise URLError("404")

    monkeypatch.setattr(
        "healpy.sphtfunc.data.get_pkg_data_filename",
        raise_url_error,
    )
    with pytest.raises(
        ValueError, match="Pixel window file for nside 16384 is not available remotely"
    ):
        hp.pixwin(16384)
