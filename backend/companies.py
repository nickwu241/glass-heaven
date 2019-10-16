#!/usr/bin/env python3
"""
./companies.py --help
usage: companies.py [-h] [-c] [-n N_COMPANIES]

optional arguments:
  -h, --help            show this help message and exit
  -c, --use-cache
  -n N_COMPANIES, --n-companies N_COMPANIES

# For logging to a file, use:
# ./companies.py | tee companies.log
"""

import argparse
import os
import sys
from typing import List, Set, Tuple

import scraper
import transformers
from models import Company, FailedCompanyError


def scrape_companies_data(
    company_names: List[str],
    use_cache: bool = False,
    n: int = float('inf'),
    skip_companies: Set[str] = set()
) -> Tuple[List[Company], List[FailedCompanyError]]:
    errors = []
    output_data = []

    for i, company_name in enumerate(company_names):
        if i >= n:
            break

        if company_name in skip_companies:
            print(f'[INFO] Skip scraping {company_name}')
            continue

        try:
            company_id = company_name.replace(' ', '_').lower()
            company = Company(id=company_id)
            overview_url, reviews_url = scraper.get_glassdoor_urls(company_name)
            print('[INFO]', company_name, overview_url, reviews_url)
            if overview_url is None or reviews_url is None:
                raise Exception(f'Cannot find both URLs for "{company_name}": {overview_url} {reviews_url}')

            reviews_data = scraper.scrape(
                reviews_url, f'{company_name}_reviews.html', scraper.get_reviews_data)
            overview_data = scraper.scrape(
                overview_url, f'{company_name}_overview.html', scraper.get_overview_data)
            data = {
                'name': company_name,
                'overview_url': overview_url,
                'reviews_url': reviews_url,
                'linkedin_url': scraper.get_linkedin_url(company_name),
            }
            data.update(reviews_data)
            data.update(overview_data)
            company.update_data(data)
            output_data.append(company)
        except Exception as e:
            print(f'[FAIL] caught exception when parsing "{company_name}"')
            errors.append(FailedCompanyError(
                company_name=company_name,
                exception=e,
            ))

    return output_data, errors


def print_failed_companies_errors(errors: List[FailedCompanyError]) -> None:
    if errors:
        print('------------')
        print('| FAILURES |')
        print('------------')
        for e in errors:
            print(f'[FAIL company:{e.company_name}]')
            print(e)
        print('[FAIL summary] failed to get data for:', [e.company_name for e in errors])


if __name__ == '__main__':
    with open('../tests/companies_input.txt') as f:
        companies = [l.strip() for l in f.readlines()]
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--use-cache', action='store_true')
    parser.add_argument('-n', '--n-companies', type=int, default=2147483647)
    args = parser.parse_args()

    # companies = ['A9', 'Akuna Capital', 'American Express', 'Beme', 'Bloomberg', 'Cisco', 'Cofense (PhishMe)', 'Cogo', 'Couple', 'DE Shaw', 'Drive.ai', 'DriveTime', 'Ebay', 'Fidelity', 'Flatiron', 'Github', 'HomeAway', 'Hp', 'Hubspot', 'Icims', 'Ideo', 'Industry Drive', 'Intel', 'JPMorgan',
    #              'Juniper', 'Kayak', 'LastPass', 'MailChimp', 'Medium', 'NextCapital', 'Nvidia', 'Occipital', 'Palantir', 'Pandora', 'Playstation', 'Priceline', 'Quora', 'RedHat', 'Sensus', 'Sift Science', 'StateFarm', 'Tableau', 'Usaa', 'Valve', 'Vizio', 'Walt Disney', 'Zappos', 'Zurb']
    # companies = ['AppDynamics']
    output_data, errors = scrape_companies_data(
        company_names=companies, use_cache=args.use_cache, n=args.n_companies,
    )
    transformers.write_to_tsv_output(output_data, filename='companies_output_raw.tsv')
    transformers.post_process(output_data)
    transformers.write_to_tsv_output(output_data, filename='companies_output_post.tsv')
    print_failed_companies_errors(errors)
