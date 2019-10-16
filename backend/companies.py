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
import re
import sys

import requests
from bs4 import BeautifulSoup

from models import Company, FailedCompanyError
from transformers import write_to_tsv_output, post_process

CACHE_FOLDER = '.scrape-cache'
os.makedirs(CACHE_FOLDER, exist_ok=True)


def write_soup(filename, soup):
    # errors='surrogatepass' for non UTF-8 characters: e.g. Salesforce
    filepath = os.path.join(CACHE_FOLDER, filename)
    with open(filepath, 'w', errors='surrogatepass') as f:
        f.write(str(soup))


def open_soup_from_file(filename):
    filepath = os.path.join(CACHE_FOLDER, filename)
    with open(filepath) as f:
        return BeautifulSoup(f.read(), 'html.parser')
    raise ValueError(f'Error opening {filename} does not exist')


def get_soup(url, cached_filename=None):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    }
    response = requests.get(url, headers=request_headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    if cached_filename:
        write_soup(cached_filename, soup)
    return soup


def scrape(url, cached_filename, callback, use_cache=False):
    if use_cache:
        soup = open_soup_from_file(cached_filename)
    else:
        soup = get_soup(url, cached_filename=cached_filename)
    return callback(soup)


def get_google_search_soup(query):
    query = query.replace(' ', '+')
    query_underscore_separated = query.replace('+', '_').lower()
    return get_soup(
        f'https://www.google.com/search?q={query}',
        cached_filename=f'google_{query_underscore_separated}.html'
    )


def get_linkedin_url(company, linkedin_url_re=re.compile(r'https://www.linkedin.com/company/\w+/')):
    soup = get_google_search_soup(f'{company}+linkedin')
    for a in soup.find_all('a'):
        url = a.get('href', '')
        match = linkedin_url_re.search(url)
        if match:
            return match.group(0)
    return None


def get_glassdoor_urls(company):
    def find_links_from_a_elements(all_a):
        overview_url = reviews_url = None
        for a in all_a:
            if overview_url and reviews_url:
                break

            url = a.get('href', '')
            if ('glassdoor.com/' not in url and 'glassdoor.ca/' not in url):
                continue

            if not overview_url and 'Overview' in url or (a.find('div') and a.find('div').text.strip().startswith('Working at')):
                overview_url = url

            if not reviews_url and 'Reviews' in url and 'Employee-Review' not in url:
                reviews_url = url

        return overview_url, reviews_url

    soup = get_google_search_soup(f'{company}+glassdor')
    overview_url, reviews_url = find_links_from_a_elements(soup.find_all('a'))
    if overview_url is None:
        soup = get_google_search_soup(f'{company}+overview+glassdor')
        overview_url, _ = find_links_from_a_elements(soup.find_all('a'))
    if reviews_url is None:
        soup = get_google_search_soup(f'{company}+reviews+glassdor')
        _, reviews_url = find_links_from_a_elements(soup.find_all('a'))

    if overview_url is None or reviews_url is None:
        raise Exception(f'Cannot find both URLs for "{company}": {overview_url} {reviews_url}')

    return overview_url, reviews_url


def get_overview_data(soup):
    divs = soup.find_all('div', class_='infoEntity')
    info = {}
    for div in divs:
        label_text = div.find('label').text.strip()
        value_text = div.find('span').text.strip()
        info[label_text] = value_text

    img = soup.select_one('span.sqLogo.tighten.lgSqLogo.logoOverlay img')
    info['Logo URL'] = img.get('src', '')

    keys = ('Website', 'Headquarters', 'Part of', 'Size', 'Founded',
            'Type', 'Industry', 'Revenue', 'Competitors', 'Logo URL')
    if len(info) > len(keys):
        unexpected_keys = info.keys() - set(keys)
        print('[FAIL ASSERT] unexpected keys for company "{}": {}'.format(info['Website'], unexpected_keys))

    for key in keys:
        if key not in info:
            info[key] = None
    return info


def get_reviews_data(soup):
    div = soup.find('div', id='EmpStats')
    review_counts = div.find('span', class_='count').text.strip()
    rating = div.find(
        'div', class_='common__EIReviewsRatingsStyles__ratingNum').text.strip()
    # Rating, Review Counts
    return {'rating': rating, 'review_counts': review_counts}


def scrape_companies_data(companies=[], use_cache=False, n=float('inf'), skip_companies=set()):
    errors = []
    output_data = []

    for i, company_name in enumerate(companies):
        try:
            if i >= n:
                break

            if company_name in skip_companies:
                print('[SKIP]', company_name)
                continue
            company_id = company_name.replace(' ', '_').lower()
            company = Company(id=company_id)
            overview_url, reviews_url = get_glassdoor_urls(company_name)
            print('[INFO]', company_name, overview_url, reviews_url)

            reviews_data = scrape(reviews_url, f'{company_name}_reviews.html', get_reviews_data)
            overview_data = scrape(overview_url, f'{company_name}_overview.html', get_overview_data)
            data = {
                'name': company_name,
                'overview_url': overview_url,
                'reviews_url': reviews_url,
                'linkedin_url': get_linkedin_url(company_name),
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


def print_failed_companies_errors(errors):
    if errors:
        print('------------')
        print('| FAILURES |')
        print('------------')
        for e in errors:
            print(f'[FAIL company:{e.company_name}]')
            print(e)
        print('[FAIL summary] failed to get data for:', [e.company_name for e in errors])


def get_intern_supply(use_cache=True):
    if use_cache:
        soup = open_soup_from_file('intern_supply.html')
    else:
        soup = get_soup('https://intern.supply/', cached_filename='intern_supply.html')

    for p in soup.select('div.company-row p.title'):
        print(p.text.strip())


if __name__ == '__main__':
    with open('../tests/companies_input.txt') as f:
        companies = [l.strip() for l in f.readlines()]
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--use-cache', action='store_true')
    parser.add_argument('-n', '--n-companies', type=int, default=2147483647)
    args = parser.parse_args()

    # get_intern_supply()
    # companies = ['A9', 'Akuna Capital', 'American Express', 'Beme', 'Bloomberg', 'Cisco', 'Cofense (PhishMe)', 'Cogo', 'Couple', 'DE Shaw', 'Drive.ai', 'DriveTime', 'Ebay', 'Fidelity', 'Flatiron', 'Github', 'HomeAway', 'Hp', 'Hubspot', 'Icims', 'Ideo', 'Industry Drive', 'Intel', 'JPMorgan',
    #              'Juniper', 'Kayak', 'LastPass', 'MailChimp', 'Medium', 'NextCapital', 'Nvidia', 'Occipital', 'Palantir', 'Pandora', 'Playstation', 'Priceline', 'Quora', 'RedHat', 'Sensus', 'Sift Science', 'StateFarm', 'Tableau', 'Usaa', 'Valve', 'Vizio', 'Walt Disney', 'Zappos', 'Zurb']
    # companies = ['AppDynamics']
    output_data, errors = scrape_companies_data(
        companies=companies, use_cache=args.use_cache, n=args.n_companies,
    )
    write_to_tsv_output(output_data, filename='companies_output_raw.tsv')
    post_process(output_data)
    write_to_tsv_output(output_data, filename='companies_output_post.tsv')
    print_failed_companies_errors(errors)
