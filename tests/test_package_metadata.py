from importlib.metadata import version

import cavebot


def test_distribution_and_package_versions_match() -> None:
    assert version("cavebot") == cavebot.__version__
