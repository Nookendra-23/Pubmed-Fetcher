Aganitha PubMed Paper Fetcher
![alt text](https://img.shields.io/pypi/v/aganitha-pubmed-fetcher)
![alt text](https://img.shields.io/pypi/pyversions/aganitha-pubmed-fetcher)
![alt text](https://img.shields.io/badge/license-MIT-blue.svg)
A command-line tool to fetch research papers from PubMed based on a user-specified query. The program filters the results to identify papers with at least one author affiliated with a pharmaceutical or biotech company.
Project Overview
This tool provides a streamlined way to search the vast PubMed database and isolate research relevant to the corporate life sciences sector. It uses the NCBI E-utilities API to perform searches, fetches detailed records, and parses author affiliation data to find matches against a heuristic that identifies non-academic institutions.
The final output is a clean, structured CSV file or a console printout, ready for analysis.
Installation
This project is managed with Poetry. Ensure you have Git and Poetry installed before proceeding.
Clone the repository:
Generated bash
git clone https://github.com/your-username/aganitha-pubmed-fetcher.git
Use code with caution.
Bash
Navigate to the project directory:
Generated bash
cd aganitha-pubmed-fetcher
Use code with caution.
Bash
Install dependencies:
This command creates a virtual environment and installs all necessary libraries specified in the pyproject.toml file.
Generated bash
poetry install
Use code with caution.
Bash
Usage
The program is run via the get-papers-list command, executed through Poetry.
Command Structure
Generated bash
poetry run get-papers-list [QUERY] --email [YOUR_EMAIL] [OPTIONS]
Use code with caution.
Bash
Arguments and Options
query (Positional, Required): The search term to use for the PubMed query. Should be enclosed in quotes if it contains spaces.
-e, --email (Required): Your email address. The NCBI API requires an email for identification with all requests.
-f, --file (Optional): The filename for the output CSV file. If this option is not provided, the results will be printed directly to the console.
-d, --debug (Optional): A flag to enable verbose debug logging, which shows detailed information about the execution process.
-h, --help: Displays the help message with information about all commands and options.
Examples
1. Basic search, printing results to the console:
Generated bash
poetry run get-papers-list "crispr gene editing" --email "your.name@example.com"
Use code with caution.
Bash
2. Search for papers on a specific disease and save the output to a CSV file:
Generated bash
poetry run get-papers-list "alzheimer's disease therapeutics" -e "your.name@example.com" -f alzheimers_papers.csv
Use code with caution.
Bash
3. Perform a search with debug mode enabled to see detailed logs:
Generated bash
poetry run get-papers-list "CAR-T cell therapy" -e "your.name@example.com" -f car-t.csv -d
Use code with caution.
Bash
Code Organization
The project follows a standard Python project structure with a src layout to ensure a clean separation between the core library module and other files.
Generated code
aganitha-pubmed-fetcher/
├── pyproject.toml          # Project metadata, dependencies, and script definitions
├── README.md               # This documentation file
├── src/
│   └── aganitha_pubmed_fetcher/
│       ├── __init__.py
│       ├── core.py         # Core logic: API calls, parsing, and filtering
│       └── cli.py          # Command-line interface logic (argparse, output handling)
└── tests/
    └── ...                 # Unit and integration tests


core.py: This is the engine of the application. It contains all the business logic for interacting with the PubMed API (fetch_pmids, fetch_paper_details), parsing the complex XML response (parse_paper_details), and identifying non-academic affiliations. Its main public-facing function is find_pharma_papers.
cli.py: This file contains all the code related to the command-line user interface. It uses Python's argparse module to define and handle arguments, calls the find_pharma_papers function from the core module, and formats the final output for either the console or a CSV file.
Tools and Libraries Used
This project was built with the help of several key tools and libraries:
Poetry: Used for dependency management, packaging, and managing the project's virtual environment.
Requests: For making robust and simple HTTP requests to the PubMed API.
Pandas: Used for structuring the final data into a DataFrame and exporting it to a CSV file.
Python Standard Library: The argparse, logging, and xml.etree.ElementTree modules were used for the CLI, logging, and XML parsing, respectively.
Development Assistance
This project was developed with the assistance of a Large Language Model (LLM). The development process, including ideation, code generation, debugging, and documentation, was guided by the conversation linked below.
LLM Conversation Link: [Paste the full public link to your conversation with the LLM here]