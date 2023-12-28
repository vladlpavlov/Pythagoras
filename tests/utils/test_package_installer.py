import random
import string

import pytest

from pythagoras._utils.package_installer import (install_package
    , uninstall_package, PackageInstallerError)

def test_actual_package():
    """Test the package installer.
    """
    actual_package_name = "nothing"

    install_package(actual_package_name)
    install_package(actual_package_name)

    uninstall_package(actual_package_name)
    uninstall_package(actual_package_name)

def test_nonexisting_package():
    """Test the package installer.
    """
    nonexisting_package_name = ""
    for i in range(20):
        nonexisting_package_name += random.choice(string.ascii_letters)
        nonexisting_package_name += random.choice(string.digits)

    with pytest.raises(PackageInstallerError):
        install_package(nonexisting_package_name)

    uninstall_package(nonexisting_package_name)