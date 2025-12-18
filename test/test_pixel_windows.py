import shutil
from pathlib import Path

import pytest
from astropy.utils import data

DATAURL = "https://healpy.github.io/healpy-data/"
DATAURL_MIRROR = "https://github.com/healpy/healpy-data/releases/download/"


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
    filename = f"pixel_window_functions/pixel_window_n{nside:04d}.fits"
    try:
        with data.conf.set_temp("dataurl", DATAURL), data.conf.set_temp(
            "dataurl_mirror", DATAURL_MIRROR
        ), data.conf.set_temp("remote_timeout", 30):
            remote_file = data.get_pkg_data_filename(filename, package="healpy")
    except OSError as err:
        pytest.skip(f"Cannot retrieve pixel window test data: {err}")

    local_file = datapath / Path(filename).name
    shutil.copy(remote_file, local_file)
    pw = hp.pixwin(nside, datapath=tmp_path)
    assert pw is not None
    assert len(pw) == 3 * nside - 1 + 1
