import os

import gdrivefs
import pytest

testdir = "gdrivefs/testdir"


@pytest.fixture()
def creds():
    tfile = os.getenv("GDRIVEFS_USER_CREDENTIALS_PATH") or None
    fs = gdrivefs.GoogleDriveFileSystem(token="cache", tokens_file=tfile)
    if fs.exists(testdir):
        fs.rm(testdir, recursive=True)
    fs.mkdir(testdir, create_parents=True)
    try:
        yield tfile
    finally:
        try:
            fs.rm(testdir, recursive=True)
        except IOError:
            pass


def test_create_anon():
    fs = gdrivefs.GoogleDriveFileSystem(token="anon")
    assert fs.service is not None


@pytest.mark.integration
def test_simple(creds):
    fs = gdrivefs.GoogleDriveFileSystem(token="cache", tokens_file=creds)
    assert fs.ls("")
    data = b"hello"
    fn = testdir + "/testfile"
    with fs.open(fn, "wb") as f:
        f.write(data)
    assert fs.cat(fn) == data


@pytest.mark.xfail(reason="Seems to be broken")
@pytest.mark.integration
def test_create_directory(creds):
    fs = gdrivefs.GoogleDriveFileSystem(token="cache", tokens_file=creds)
    fs.makedirs(testdir + "/data")
    fs.makedirs(testdir + "/data/bar/baz")

    assert fs.exists(testdir + "/data")
    assert fs.exists(testdir + "/data/bar")
    assert fs.exists(testdir + "/data/bar/baz")

    data = b"intermediate path"
    with fs.open(testdir + "/data/bar/test", "wb") as f:
        f.write(data)
    assert fs.cat(testdir + "/data/bar/test") == data
