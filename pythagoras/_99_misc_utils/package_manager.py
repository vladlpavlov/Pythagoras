import subprocess
import importlib
import sys
from typing import Optional

from pythagoras._01_foundational_objects.basic_exceptions import PythagorasException

class PackageInstallerError(PythagorasException):
    pass

def install_package(package_name:str
        , upgrade:bool=False
        , version:Optional[str]=None
        ) -> None:
    """Install package using pip."""
    command = [sys.executable, "-m", "pip", "install"]

    if upgrade:
        command += ["--upgrade"]

    package_spec = f"{package_name}=={version}" if version else package_name
    command += [package_spec]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE
            , stderr=subprocess.STDOUT, text=True)

    except subprocess.CalledProcessError as e:
        raise PackageInstallerError(
            f"Failed to install package '{package_spec}'. "
            +f"Error output:\n{e.stdout}")
    try:
        importlib.import_module(package_name)
    except Exception as e:
        raise PackageInstallerError(
            f"Failed to validate package installation'{package_spec}'. "
            +f"Error output:\n{result.stdout}")

def uninstall_package(package_name:str)->None:
    """Uninstall package using pip."""
    command = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE
            , stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise PackageInstallerError(
            f"Failed to uninstall package '{package_name}'. "
            +f"Error output:\n{e.stdout}")
    try:
        package = importlib.import_module(package_name)
        importlib.reload(package)
    except:
        pass
    else:
        raise PackageInstallerError(
            f"Failed to validate package uninstallation for '{package_name}'. ")