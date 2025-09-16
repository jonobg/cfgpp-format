from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cfgpp",
    version="0.1.0",
    author="CFGPP Development Team",
    author_email="dev@cfgpp.org",
    description="A robust configuration parser for the CFGPP format - industrial-grade config management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonobg/cfgpp-format",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "antlr4-python3-runtime>=4.13.1",
        "pyyaml>=5.4.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=22.12.0",
            "mypy>=1.1.1",
            "pylint>=2.17.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "cfgpp=cfgpp.cli:main",
        ],
    },
)
