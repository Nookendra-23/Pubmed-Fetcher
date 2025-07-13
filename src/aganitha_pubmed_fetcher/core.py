# src/aganitha_pubmed_fetcher/core.py

"""
Core module for fetching and processing data from the PubMed API.
"""

import requests
import logging
import xml.etree.ElementTree as ET
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Set, Dict, Any

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# constants for URLs and tool identification.
PUBMED_API_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL_NAME = "aganitha_pubmed_fetcher"

NON_ACADEMIC_KEYWORDS: Set[str] = {
    "inc", "ltd", "llc", "corp", "pharmaceuticals", "pharma", "biotech",
    "therapeutics", "diagnostics", "labs", "laboratories"
}
ACADEMIC_KEYWORDS: Set[str] = {
    "university", "college", "institute", "hospital", "school", "academic", "univerzita"
}

# Defined a dataclass for structured paper information.
# This makes the output type explicit and easy to use.
@dataclass
class PaperData:
    """A structured representation of a research paper's data."""
    pubmed_id: str
    title: str
    publication_date: str
    non_academic_authors: List[str] = field(default_factory=list)
    company_affiliations: List[str] = field(default_factory=list)
    corresponding_author_email: Optional[str] = None

def _is_non_academic(affiliation: str) -> bool:
    """
    Determines if an affiliation is non-academic based on keywords.

    Heuristic:
    1. If it contains academic keywords (e.g., 'University'), it's academic.
    2. Otherwise, if it contains corporate keywords (e.g., 'Inc', 'Pharma'),
       it's considered non-academic.

    Args:
        affiliation: The affiliation string to check.

    Returns:
        True if the affiliation is likely non-academic, False otherwise.
    """
    if not affiliation:
        return False

    lower_aff = affiliation.lower()

    # If it contains a strong academic signal, rule it out immediately.
    if any(word in lower_aff for word in ACADEMIC_KEYWORDS):
        return False

    # If it contains a strong corporate signal, flag it as non-academic.
    if any(word in lower_aff for word in NON_ACADEMIC_KEYWORDS):
        return True

    # Default to False if no clear signal is found.
    return False

def fetch_pmids(
    query: str,
    email: str,
    max_results: int = 100,
) -> List[str]:
    """
    Fetches a list of PubMed IDs (PMIDs) for a given search query.

    This function calls the PubMed eSearch API to find articles matching the
    query and returns their unique identifiers.

    Args:
        query: The search term to use for the PubMed query (e.g., "cancer therapy").
        email: The user's email address. Providing an email is a requirement
               of the NCBI E-utilities to identify users.
        max_results: The maximum number of PMIDs to return.

    Returns:
        A list of strings, where each string is a PubMed ID (PMID).
        Returns an empty list if no results are found.

    Raises:
        ConnectionError: If there is a network-related issue (e.g., DNS failure,
                         refused connection) or an HTTP error status code (4xx/5xx).
        ValueError: If the API response is not in the expected JSON format or
                    lacks the required keys ('esearchresult' or 'idlist').
    """
    esearch_url = f"{PUBMED_API_BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(max_results),  # API parameters are strings
        "tool": TOOL_NAME,
        "email": email,
    }

    logging.info(f"Executing eSearch for query: '{query}'")

    try:
        response = requests.get(esearch_url, params=params, timeout=15)
        # This will raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {e}"
        logging.error(error_message)
        # Re-raise as a ConnectionError to abstract the implementation detail
        raise ConnectionError(error_message) from e

    try:
        data = response.json()
        esearch_result = data.get("esearchresult")

        if not esearch_result:
            raise ValueError("Invalid API response: 'esearchresult' key is missing.")

        # If no articles are found, the 'idlist' can be missing.
        # This is a valid case, not an error.
        pmid_list: List[str] = esearch_result.get("idlist", [])
        logging.info(f"Found {len(pmid_list)} PMIDs for the query.")
        return pmid_list

    except (ValueError, KeyError) as e:
        # Catches JSON decoding errors or if 'esearchresult' is not a dict
        error_message = f"Failed to parse API response: {e}. Response text: {response.text[:200]}..."
        logging.error(error_message)
        raise ValueError(error_message) from e
    


def fetch_paper_details(pmids: List[str], email: str) -> str:
    """
    Fetches the full XML records for a list of PubMed IDs (PMIDs).

    This function calls the PubMed eFetch API. For robustness, this function
    uses a POST request, which is the preferred method for long lists of IDs to
    avoid URL length limits.

    Args:
        pmids: A list of PubMed ID strings to fetch details for.
        email: The user's email address for NCBI API identification.

    Returns:
        A string containing the raw XML data of the fetched records as returned
        by the API. Returns an empty string if the input list of PMIDs is empty.

    Raises:
        ConnectionError: If there is a network-related issue or an HTTP
                         error status code (4xx/5xx) during the API call.
    """
    if not pmids:
        logging.info("PMID list is empty. Skipping eFetch call.")
        return ""

    efetch_url = f"{PUBMED_API_BASE_URL}efetch.fcgi"

    # Data payload for the POST request.
    # Joining the list of PMIDs into a single comma-separated string.
    data_payload = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",  # We want the data in a structured XML format.
        "tool": TOOL_NAME,
        "email": email,
    }

    logging.info(f"Executing eFetch for {len(pmids)} PMIDs.")

    try:
        # Using a POST request is safer for potentially long lists of IDs.
        # We also increase the timeout slightly as fetching full records can take longer.
        response = requests.post(efetch_url, data=data_payload, timeout=30)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed during eFetch: {e}"
        logging.error(error_message)
        raise ConnectionError(error_message) from e

    # The response text contains the XML data we requested.
    xml_data: str = response.text
    logging.info(f"Successfully fetched details. XML data length: {len(xml_data)}")

    return xml_data


def parse_paper_details(xml_data: str) -> List[PaperData]:
    """
    Parses an XML string from PubMed eFetch and extracts paper details.

    This function iterates through each article in the XML, extracts the
    required fields, and applies a heuristic to identify authors affiliated
    with non-academic institutions. It only returns papers that have at least
    one such author.

    Args:
        xml_data: A string containing the XML data from an eFetch API call.

    Returns:
        A list of PaperData objects for papers that match the non-academic
        author criteria. Returns an empty list if no matching papers are found
        or if the input is empty.
    """
    if not xml_data:
        return []

    root = ET.fromstring(xml_data)
    papers_with_company_authors: List[PaperData] = []
    email_regex = re.compile(r'[\w\.\-]+@[\w\.\-]+')

    for article_node in root.findall('.//PubmedArticle'):
        # --- Basic Information Extraction (with None-safety) ---
        pmid_node = article_node.find('.//PMID')
        pmid = pmid_node.text if pmid_node is not None else "N/A"

        title_node = article_node.find('.//ArticleTitle')
        # Titles can be complex XML; join all text parts.
        title = "".join(title_node.itertext()) if title_node is not None else "No Title Found"

        # --- Date Extraction ---
        pub_date_node = article_node.find('.//PubDate')
        if pub_date_node is not None:
            year = pub_date_node.findtext('Year', 'YYYY')
            month = pub_date_node.findtext('Month', 'MM')
            day = pub_date_node.findtext('Day', 'DD')
            publication_date = f"{year}-{month}-{day}"
        else:
            publication_date = "No Date Found"

        # --- Author, Affiliation, and Email Logic ---
        non_academic_authors: Set[str] = set()
        company_affiliations: Set[str] = set()
        corresponding_email: Optional[str] = None
        
        author_list_node = article_node.find('.//AuthorList')
        if author_list_node is not None:
            for author_node in author_list_node.findall('.//Author'):
                # Handle different author types (individual vs. collective)
                collective_name_node = author_node.find('CollectiveName')
                if collective_name_node is not None and collective_name_node.text:
                    author_name = collective_name_node.text
                else:
                    lastname_node = author_node.find('LastName')
                    forename_node = author_node.find('ForeName')
                    
                    # Check if nodes exist before accessing .text
                    forename = forename_node.text if forename_node is not None else ""
                    lastname = lastname_node.text if lastname_node is not None else ""
                    author_name = f"{forename} {lastname}".strip()

                affiliation_node = author_node.find('.//Affiliation')
                if affiliation_node is not None and affiliation_node.text:
                    affiliation_text = "".join(affiliation_node.itertext())
                    
                    # Apply the heuristic to check the affiliation
                    if _is_non_academic(affiliation_text):
                        if author_name:
                            non_academic_authors.add(author_name)
                        company_affiliations.add(affiliation_text.strip())

                    # Search for an email address in the affiliation text
                    if not corresponding_email:
                        match = email_regex.search(affiliation_text)
                        if match:
                            corresponding_email = match.group(0)

        # --- Final Assembly and Filtering ---
        # Only include papers that have at least one non-academic author.
        if non_academic_authors:
            paper = PaperData(
                pubmed_id=pmid,
                title=title,
                publication_date=publication_date,
                non_academic_authors=sorted(list(non_academic_authors)),
                company_affiliations=sorted(list(company_affiliations)),
                corresponding_author_email=corresponding_email,
            )
            papers_with_company_authors.append(paper)

    logging.info(f"Parsed {len(papers_with_company_authors)} papers with non-academic authors.")
    return papers_with_company_authors



def find_pharma_papers(
    query: str,
    email: str,
    max_results: int = 100,
) -> List[Dict[str, Any]]:
    """
    Finds research papers matching a query with at least one non-academic author.

    This is the main public-facing function of the module. It orchestrates the
    entire process:
    1. Fetches PubMed IDs (PMIDs) for the query.
    2. Fetches the detailed XML records for those PMIDs.
    3. Parses the records, filtering for papers with non-academic affiliations.
    4. Converts the results into a user-friendly list of dictionaries.

    Args:
        query: The search term for the PubMed query (e.g., "crispr gene editing").
        email: The user's email address, required for NCBI API access.
        max_results: The maximum number of papers to fetch from the initial search.

    Returns:
        A list of dictionaries. Each dictionary represents a paper and contains
        keys like 'pubmed_id', 'title', 'non_academic_authors', etc.
        Returns an empty list if no matching papers are found.

    Raises:
        ConnectionError: If any API call fails due to network issues.
        ValueError: If the API response is malformed or cannot be parsed.
    """
    logging.info(f"Starting pharma paper search for query: '{query}'")

    # Step 1: Fetch PMIDs for the given query.
    pmids = fetch_pmids(query=query, email=email, max_results=max_results)

    if not pmids:
        logging.info("No PMIDs found for the query. No further action taken.")
        return []

    # Step 2: Fetch the full paper details for the found PMIDs.
    xml_data = fetch_paper_details(pmids=pmids, email=email)

    if not xml_data:
        logging.warning("Received empty XML data from eFetch. No papers to parse.")
        return []

    # Step 3: Parse the XML data to get structured PaperData objects.
    # This step also performs the filtering for non-academic authors.
    parsed_papers: List[PaperData] = parse_paper_details(xml_data)

    # Step 4: Convert the list of dataclass objects into a list of dictionaries.
    # dataclasses.asdict is a convenient helper for this conversion.
    results: List[Dict[str, Any]] = [asdict(paper) for paper in parsed_papers]

    logging.info(f"Process complete. Returning {len(results)} filtered papers.")
    return results


