Aganitha PubMed Paper Fetcher
![alt text](https://img.shields.io/badge/License-MIT-blue.svg)
![alt text](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![alt text](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)
A powerful command-line tool to fetch research papers from PubMed and filter for authors affiliated with pharmaceutical or biotech companies.
<!--
**PRO-TIP:** Record a short GIF of you running the command and showing the output. It's the best way to demonstrate your project. You can use free tools like LICEcap or ScreenToGif.
-->
A brief demonstration of the get-papers-list command.
✨ Features
Direct PubMed Integration: Uses the NCBI E-utilities API to perform powerful, flexible queries.
Intelligent Company Filtering: Implements a smart heuristic to identify authors from non-academic institutions (pharma, biotech, etc.).
Flexible Output: Choose to print results in a clean table directly to your console or save them as a structured CSV file.
User-Friendly CLI: A simple and intuitive command-line interface built with Python's standard argparse module.
Modern Python Tooling: Built with Poetry for dependency management and packaging.
🚀 Installation
Getting started is simple. Ensure you have Git and Poetry installed.
Clone the Repository:
Generated bash
git clone https://github.com/your-username/aganitha-pubmed-fetcher.git
Use code with caution.
Bash
Navigate to the Project Directory:
Generated bash
cd aganitha-pubmed-fetcher
Use code with caution.
Bash
Install Dependencies with Poetry:
This command will create a dedicated virtual environment and install all required libraries.
Generated bash
poetry install
Use code with caution.
Bash
💻 Usage
The tool is run via the get-papers-list command, executed through Poetry.
Command Structure
Generated bash
poetry run get-papers-list [QUERY] --email [YOUR_EMAIL] [OPTIONS]
Use code with caution.
Bash
Arguments & Options
Argument	Flag(s)	Required?	Description
query	(Positional)	Yes	The search term for PubMed (e.g., "cancer therapy").
email	-e, --email	Yes	Your email address (required by the NCBI API for access).
file	-f, --file	No	Output CSV filename. If omitted, prints results to the console.
debug	-d, --debug	No	Flag to enable verbose debug logging for detailed output.
help	-h, --help	No	Displays the help message with all options.
Examples
1. Search and Print to Console
This is the most direct way to get results.
Generated bash
poetry run get-papers-list "crispr gene editing" --email "your.name@example.com"
Use code with caution.
Bash
2. Search and Save to a CSV File
Use the -f flag to specify your output file.
Generated bash
poetry run get-papers-list "alzheimer's disease therapeutics" -e "your.name@example.com" -f alzheimers_papers.csv
Use code with caution.
Bash
3. Run a Search with Debug Mode
Enable the -d flag to see detailed execution logs, which is helpful for troubleshooting.
Generated bash
poetry run get-papers-list "CAR-T cell therapy" -e "your.name@example.com" -f car-t.csv -d
Use code with caution.
Bash
🏗️ Code Architecture
The project uses a standard src layout for a clean separation between the application code and other files.
Generated code
aganitha-pubmed-fetcher/
├── pyproject.toml          # Project metadata, dependencies, and script definitions
├── README.md               # This documentation file
├── src/
│   └── aganitha_pubmed_fetcher/
│       ├── __init__.py
│       ├── core.py         # Core logic: API calls, parsing, and filtering
│       └── cli.py          # Command-line interface logic and output handling
└── .gitignore              # Specifies files for Git to ignore
Use code with caution.
core.py: The "engine" of the application. It handles all communication with the PubMed API, parses the XML responses, and filters the data based on the non-academic author heuristic.
cli.py: The "user interface." It handles parsing command-line arguments, calling the core logic, and formatting the final output for the user (either as a console table or a CSV file).
⚙️ How It Works
The program follows a clear, sequential pipeline to get from a query to the final results:
eSearch: Takes the user's query and gets a list of matching PubMed IDs (PMIDs).
eFetch: Takes the list of PMIDs and fetches the full, detailed XML records for all of them in a single API call.
Parse: Reads the complex XML data, carefully extracting the title, publication date, authors, and affiliations for each paper.
Filter: Applies the non-academic heuristic to each author's affiliation. If a paper has at least one author from a corporate institution, it is kept.
Output: The final, filtered list of papers is converted into a pandas DataFrame and then either written to a CSV file or printed to the console.
🛠️ Tools & Acknowledgements
Poetry: For dependency management and packaging.
Requests: For making robust HTTP requests.
Pandas: For powerful data manipulation and CSV export.
AI Assistance: This project was developed with the help of an AI assistant (DeepSeek). The LLM was used for brainstorming complex logic, debugging specific errors, and refining code structure. The full development conversation can be viewed here: