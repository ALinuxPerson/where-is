from typing import List, Dict
import setuptools  # type: ignore
import pathlib

REQUIRED: List[str] = ["rich==3.1.0", "fire==0.3.1"]
EXTRAS: Dict[str, List[str]] = {"dev": ["mypy==0.782"]}

setuptools.setup(
    name="where-is",
    version=pathlib.Path("VERSION").read_text().strip(),
    description="Finds config files.",
    long_description=pathlib.Path("README.md").read_text().strip(),
    author="ALinuxPerson",
    author_email="micheal02052007@gmail.com",
    python_requires=">=3.6.0",
    packages=setuptools.find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    entry_points={"console_scripts": ["where-is=whereis.__main__:main"]},
    include_package_data=True,
    license="GNU GPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
    ],
)
