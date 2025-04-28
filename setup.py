from setuptools import setup, find_packages

setup(
    name="audiblescrapernct",
    version="0.1.0",
    description="A Python package to scrape Audible libraries and export them to JSON or Word/PDF/HTML.",
    author="Nel Prinsloo",
    author_email="nel@nelcapetown.com",
    url="https://github.com/NelCapeTown/PythonAudibleScraperNCT",  # (optional for now)
    packages=find_packages(),  # Automatically include all packages (like audiblescraper/)
    install_requires=[
        "playwright",
        "openpyxl",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",   # (or choose another)
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
