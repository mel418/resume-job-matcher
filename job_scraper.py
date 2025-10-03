#!/usr/bin/env python3
"""
Job Scraper - Extract job descriptions from URLs
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from anthropic import Anthropic


def is_url(text: str) -> bool:
    """Check if the text is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(text) is not None


def extract_job_description_basic(url: str) -> str:
    """
    Basic scraper for static HTML pages.
    Returns the cleaned text content.
    """
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Fetch the page
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(['script', 'style', 'nav', 'header', 'footer']):
        script.decompose()

    # Try to find common job description containers
    job_content = None

    # Common class/id patterns for job descriptions
    common_selectors = [
        {'class': re.compile(r'job[-_]description', re.I)},
        {'class': re.compile(r'description', re.I)},
        {'class': re.compile(r'job[-_]detail', re.I)},
        {'class': re.compile(r'posting', re.I)},
        {'id': re.compile(r'job[-_]description', re.I)},
        {'id': re.compile(r'description', re.I)},
    ]

    for selector in common_selectors:
        job_content = soup.find('div', selector)
        if job_content:
            break

    # If no specific container found, try main content area
    if not job_content:
        job_content = soup.find('main') or soup.find('article') or soup.find('body')

    # Extract text
    if job_content:
        text = job_content.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)

    # Clean up the text
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)

    return cleaned_text


def extract_job_description(url: str) -> str:
    """
    Scrape job description from a URL using basic HTML parsing.
    Returns the cleaned text content or raises exception if JavaScript is required.
    """
    try:
        # Try basic scraping
        content = extract_job_description_basic(url)

        # Check if it's a JavaScript-only page
        if len(content) < 200 or 'javascript' in content.lower()[:500]:
            raise Exception(
                "Unable to scrape - site requires JavaScript to load content."
            )

        return content

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")


def extract_company_and_role(content: str, api_key: str) -> tuple[str, str]:
    """
    Use Claude to extract company name and role from job description.
    Returns tuple of (company, role).
    """
    try:
        client = Anthropic(api_key=api_key)

        prompt = f"""Extract the company name and job role/position from this job description.
Return ONLY in this exact format:
Company: [company name]
Role: [job role/position]

Job Description:
{content[:2000]}"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text.strip()

        # Parse response
        company = "Unknown"
        role = "Unknown"

        for line in response.split('\n'):
            if line.startswith('Company:'):
                company = line.replace('Company:', '').strip()
            elif line.startswith('Role:'):
                role = line.replace('Role:', '').strip()

        return company, role
    except:
        return "Unknown", "Unknown"


def save_job_description(url: str, content: str, api_key: str = None) -> str:
    """
    Save job description to a file in job-descriptions directory.
    Returns the file path.
    """
    # Create directory if it doesn't exist
    output_dir = Path('job-descriptions')
    output_dir.mkdir(exist_ok=True)

    # Extract company and role if API key provided
    if api_key:
        company, role = extract_company_and_role(content, api_key)
        # Clean filename
        company_clean = re.sub(r'[^\w\s-]', '', company).strip().replace(' ', '_')
        role_clean = re.sub(r'[^\w\s-]', '', role).strip().replace(' ', '_')
        filename = f"{company_clean}_{role_clean}.txt"
    else:
        # Fallback to domain-based naming
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '').split('.')[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.txt"

    file_path = output_dir / filename

    # Save content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"Source URL: {url}\n")
        f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(content)

    return str(file_path)


def scrape_job(url: str, api_key: str = None) -> tuple[str, str]:
    """
    Main function to scrape a job description from URL.
    Returns tuple of (file_path, content).
    """
    content = extract_job_description(url)
    file_path = save_job_description(url, content, api_key)
    return file_path, content
