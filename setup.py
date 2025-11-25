from setuptools import setup, find_packages

setup(
    name="fc26-career-analyzer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click",
        "sqlalchemy",
        "google-generativeai",
        "chromadb",
        "sentence-transformers",
        "rich",
        "python-dotenv",
        "pytest",
        "pytest-cov",
    ],
    entry_points={
        "console_scripts": [
            "fc26-analyzer=cli.main:cli",
        ],
    },
)
