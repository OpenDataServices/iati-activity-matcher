import os

import pytest


@pytest.fixture(scope="module")
def chdir_fixtures():
    original_dir = os.getcwd()
    os.chdir("tests/fixtures")
    yield
    os.chdir(original_dir)
