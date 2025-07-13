# src/aganitha_pubmed_fetcher/cli.py

import argparse
import logging
import sys
import pandas as pd
from typing import List, Dict, Any

# Import the main public function from our core module
from aganitha_pubmed_fetcher.core import find_pharma_papers, PaperData

# We will configure logging based on the --debug flag
# Get the logger for our specific application
log = logging.getLogger("aganitha_pubmed_fetcher")


def create_parser() -> argparse.ArgumentParser:
    """Creates and configures the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch PubMed research papers with authors from pharma/biotech companies.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example Usage:
-------------
# Search for papers and print results to the console
poetry run get-papers-list "crispr gene editing" --email "user@example.com"

# Search and save results to a file with debug logging
poetry run get-papers-list "alzheimer's disease therapeutics" -e "user@example.com" -f results.csv -d
"""
    )

    parser.add_argument("query", type=str, help="The search query for PubMed (e.g., 'cancer therapy').")
    parser.add_argument("-f", "--file", type=str, default=None, metavar="FILENAME", help="Output CSV filename. If not provided, prints results to the console.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging for detailed execution output.")
    parser.add_argument("-e", "--email", type=str, required=True, metavar="EMAIL_ADDRESS", help="Your email address (required by NCBI for API access).")
    
    return parser


def results_to_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """Converts the list of result dictionaries to a formatted DataFrame."""
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    # Make list columns readable in CSV/console output
    df['non_academic_authors'] = df['non_academic_authors'].apply(lambda x: ', '.join(x))
    df['company_affiliations'] = df['company_affiliations'].apply(lambda x: ', '.join(x))

    # Rename columns to match the required output headers
    df.rename(columns={
        'pubmed_id': 'PubmedID',
        'title': 'Title',
        'publication_date': 'Publication Date',
        'non_academic_authors': 'Non-academic Author(s)',
        'company_affiliations': 'Company Affiliation(s)',
        'corresponding_author_email': 'Corresponding Author Email'
    }, inplace=True)
    
    # Ensure all required columns are present and in the correct order
    output_columns = [
        'PubmedID', 'Title', 'Publication Date', 'Non-academic Author(s)',
        'Company Affiliation(s)', 'Corresponding Author Email'
    ]
    df = df.reindex(columns=output_columns)

    return df


def main():
    """The main entry point for the command-line program."""
    parser = create_parser()
    args = parser.parse_args()

    # --- 1. Configure Logging based on --debug flag ---
    log_level = logging.DEBUG if args.debug else logging.INFO
    # Configure the root logger, which our 'core' module also uses
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s', stream=sys.stdout)
    
    log.info(f"Starting search with query: '{args.query}'")
    if args.debug:
        log.debug(f"Execution arguments: {args}")
        
    try:
        # --- 2. Call the Core Logic ---
        # This is where the CLI calls the module to do the heavy lifting.
        # It passes the query and email directly from the command line.
        papers: List[Dict[str, Any]] = find_pharma_papers(query=args.query, email=args.email)

        # --- 3. Format and Output the Results ---
        if not papers:
            log.info("No papers with non-academic authors were found.")
            return

        df = results_to_dataframe(papers)

        if args.file:
            # User specified a file, so write to CSV
            log.info(f"Writing {len(df)} results to CSV file: {args.file}")
            df.to_csv(args.file, index=False)
            log.info("File saved successfully.")
        else:
            # No file specified, so print neatly to the console
            log.info("Printing results to console:")
            # Use to_string() for a clean console representation
            print(df.to_string())

    except (ConnectionError, ValueError) as e:
        log.error(f"A critical error occurred: {e}")
        sys.exit(1) # Exit with an error code

    log.info("Program finished successfully.")


if __name__ == "__main__":
    main()