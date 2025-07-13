# Aganitha PubMed Paper Fetcher

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python Version](https://img.shields.io/badge/python-3.9+-brightgreen.svg) ![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)

A powerful command-line tool to fetch research papers from PubMed and filter for authors affiliated with pharmaceutical or biotech companies.

---

## ✨ Features

*   **Direct PubMed Integration:** Uses the NCBI E-utilities API to perform powerful, flexible queries.
*   **Intelligent Company Filtering:** Implements a smart heuristic to identify authors from non-academic institutions (pharma, biotech, etc.).
*   **Flexible Output:** Choose to print results in a clean table directly to your console or save them as a structured **CSV file**.
*   **User-Friendly CLI:** A simple and intuitive command-line interface built with Python's standard `argparse` module.
*   **Modern Python Tooling:** Built with Poetry for dependency management and packaging.

## 🚀 Installation

Getting started is simple. Ensure you have [Git](https://git-scm.com/) and [Poetry](https://python-poetry.org/) installed.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/aganitha-pubmed-fetcher.git
    ```

2.  **Navigate to the Project Directory:**
    ```bash
    cd aganitha-pubmed-fetcher
    ```

3.  **Install Dependencies with Poetry:**
    This command will create a dedicated virtual environment and install all required libraries.
    ```bash
    poetry install
    ```

## 💻 Usage

The tool is run via the `get-papers-list` command, executed through Poetry.

#### **Command Structure**

```bash
poetry run get-papers-list [QUERY] --email [YOUR_EMAIL] [OPTIONS]
```
## Arguments & Options
Argument	Flag(s)	Required?	Description
query	(Positional)	Yes	The search term for PubMed (e.g., "cancer therapy").
email	-e, --email	Yes	Your email address (required by the NCBI API for access).
file	-f, --file	No	Output CSV filename. If omitted, prints results to the console.
debug	-d, --debug	No	Flag to enable verbose debug logging for detailed output.
help	-h, --help	No	Displays the help message with all options.

## Examples
1. Search and Print to Console
This is the most direct way to get results.
```bash
poetry run get-papers-list "crispr gene editing" --email "your.name@example.com"
```
3. Search and Save to a CSV File
Use the -f flag to specify your output file.
```bash
poetry run get-papers-list "alzheimer's disease therapeutics" -e "your.name@example.com" -f alzheimers_papers.csv
```
4. Run a Search with Debug Mode
Enable the -d flag to see detailed execution logs, which is helpful for troubleshooting.
```bash
poetry run get-papers-list "CAR-T cell therapy" -e "your.name@example.com" -f car-t.csv -d
```
🏗️ Code Architecture
The project uses a standard src layout for a clean separation between the application code and other files.

aganitha-pubmed-fetcher/
├── pyproject.toml          # Project metadata, dependencies, and script definitions
├── README.md               # This documentation file
├── src/
│   └── aganitha_pubmed_fetcher/
│       ├── __init__.py
│       ├── core.py         # Core logic: API calls, parsing, and filtering
│       └── cli.py          # Command-line interface logic and output handling
└── .gitignore              # Specifies files for Git to ignore

core.py: The "engine" of the application. It handles all communication with the PubMed API, parses the XML responses, and filters the data based on the non-academic author heuristic.
cli.py: The "user interface." It handles parsing command-line arguments, calling the core logic, and formatting the final output for the user (either as a console table or a CSV file).

##⚙️ How It Works
The program follows a clear, sequential pipeline to get from a query to the final results:
eSearch: Takes the user's query and gets a list of matching PubMed IDs (PMIDs).
eFetch: Takes the list of PMIDs and fetches the full, detailed XML records for all of them in a single API call.
Parse: Reads the complex XML data, carefully extracting the title, publication date, authors, and affiliations for each paper.
Filter: Applies the non-academic heuristic to each author's affiliation. If a paper has at least one author from a corporate institution, it is kept.
Output: The final, filtered list of papers is converted into a pandas DataFrame and then either written to a CSV file or printed to the console.

##🛠️ Tools & Acknowledgements
Poetry: For dependency management and packaging.
Requests: For making robust HTTP requests.
Pandas: For powerful data manipulation and CSV export.

