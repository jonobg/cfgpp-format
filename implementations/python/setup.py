from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cfgpp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python parser for the cfgpp configuration language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cfgpp-format",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyyaml>=5.4.1",
    ],
    entry_points={
        "console_scripts": [
            "cfgpp=cfgpp.cli:main",
        ],
    },
)
