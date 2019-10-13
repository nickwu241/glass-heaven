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
from time import sleep
import re
import sys

import requests
from bs4 import BeautifulSoup

LINKEDIN_URL_RE = re.compile(r'https://www.linkedin.com/company/\w+/')


def write_soup(filename, soup):
    # errors='surrogatepass' for non UTF-8 characters: e.g. Salesforce
    with open(filename, 'w', errors='surrogatepass') as f:
        f.write(str(soup))


def get_linkedin_url(company):
    r = requests.get(f'https://www.google.com/search?q={company}+linkedin')
    soup = BeautifulSoup(r.text, 'html.parser')
    write_soup(f'{company}_google_linkedin.html', soup)
    for a in soup.find_all('a'):
        url = a['href']
        match = LINKEDIN_URL_RE.search(url)
        if match:
            return match.group(0)
    return 'Unknown'


def get_url(company):
    company_dash_separated = company.replace(' ', '-')

    def find_links_from_a_elements(all_a):
        overview_url = reviews_url = None
        for a in all_a:
            if overview_url and reviews_url:
                break

            url = a['href']
            if not url.startswith('/url?q') or ('glassdoor.com/' not in url and 'glassdoor.ca/' not in url):
                continue

            if 'Overview' in url or (a.find('div') and a.find('div').text.strip().startswith('Working at')):
                clean_url = url.lstrip('/url?q=').split('&')[0]
                overview_url = clean_url

            if 'Reviews' in url and 'Employee-Review' not in url and f'{company_dash_separated}-Reviews-E' in url:
                clean_url = url.lstrip('/url?q=').split('&')[0]
                reviews_url = clean_url

        return overview_url, reviews_url

    r = requests.get(f'https://www.google.com/search?q={company}+glassdoor')
    soup = BeautifulSoup(r.text, 'html.parser')
    write_soup(f'{company}_google_1.html', soup)
    overview_url, reviews_url = find_links_from_a_elements(soup.find_all('a'))
    if overview_url is None:
        r = requests.get(f'https://www.google.com/search?q={company}+overview+glassdoor')
        soup = BeautifulSoup(r.text, 'html.parser')
        write_soup(f'{company}_google_overview.html', soup)
        overview_url, _ = find_links_from_a_elements(soup.find_all('a'))

    if reviews_url is None:
        r = requests.get(f'https://www.google.com/search?q={company}+reviews+glassdoor')
        soup = BeautifulSoup(r.text, 'html.parser')
        write_soup(f'{company}_google_reviews.html', soup)
        _, reviews_url = find_links_from_a_elements(soup.find_all('a'))

    if overview_url is None or reviews_url is None:
        raise Exception(f'Cannot find both URLs for {company}: {overview_url} {reviews_url}')

    return overview_url, reviews_url


def get_overview_data(soup):
    divs = soup.find_all('div', class_='infoEntity')
    info = {}
    for div in divs:
        label_text = div.find('label').text.strip()
        value_text = div.find('span').text.strip()
        info[label_text] = value_text

    keys = ('Website', 'Headquarters', 'Part of', 'Size', 'Founded', 'Type', 'Industry', 'Revenue', 'Competitors')
    if len(info) > len(keys):
        unexpected_keys = info.keys() - set(keys)
        print('[FAIL ASSERT] unexpected keys for company "{}": {}'.format(info['Website'], unexpected_keys))

    return [info.get(key, 'Unknown') for key in keys]


def get_reviews_data(soup):
    div = soup.find('div', id='EmpStats')
    review_counts = div.find('span', class_='count').text.strip()
    rating = div.find(
        'div', class_='common__EIReviewsRatingsStyles__ratingNum').text.strip()
    # Rating, Review Counts
    return [rating, review_counts]


def scrape_companies_data(companies=[], use_cache=False, n=float('inf'), skip_companies=set()):
    failed_companies = []
    output_data = [
        [
            'Name', 'Rating', 'Review Counts', 'Website', 'Headquarters', 'Part of',
            'Size', 'Founded', 'Type', 'Industry', 'Revenue', 'Competitors',
            'Overview URL', 'Reviews URL', 'LinkedIn URL',
        ]
    ]
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    }
    for i, company in enumerate(companies):
        try:
            if company in skip_companies:
                print('[SKIP]', company)
                continue
            print('[INFO]', company)
            overview_url, reviews_url = get_url(company)
            print('[INFO]', company, overview_url, reviews_url)
            if i > n:
                break

            elif use_cache:
                with open(f'{company}_reviews.html') as f:
                    reviews_soup = BeautifulSoup(f.read(), 'html.parser')

                with open(f'{company}_overview.html') as f:
                    overview_soup = BeautifulSoup(f.read(), 'html.parser')
            else:
                reviews_r = requests.get(reviews_url, headers=request_headers)
                reviews_soup = BeautifulSoup(reviews_r.text, 'html.parser')
                write_soup(f'{company}_reviews.html', reviews_soup)

                overview_r = requests.get(overview_url, headers=request_headers)
                overview_soup = BeautifulSoup(overview_r.text, 'html.parser')
                write_soup(f'{company}_overview.html', overview_soup)
                # sleep(0.5)

            reviews_data = get_reviews_data(reviews_soup)
            overview_data = get_overview_data(overview_soup)
            linkedin_data = [get_linkedin_url(company)]
            output = [company] + reviews_data + overview_data + [overview_url, reviews_url] + linkedin_data
            output_data.append(output)
        except Exception as e:
            print(f'[FAIL] unable to parse data for {company}')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            failed_companies.append([company, e, exc_tb.tb_lineno])

    return output_data, failed_companies


def write_to_tsv_output(output_data, filename):
    output_data_iter = iter(output_data)
    tsv_lines = []
    tsv_lines.append('\t'.join(next(output_data_iter)) + '\n')
    for line in output_data_iter:
        tsv_lines.append('\t'.join(line) + '\n')

    with open(filename, 'w') as f:
        f.writelines(tsv_lines)
    print(f'[INFO] wrote data to {filename}')


def print_failed_companies(failed_companies):
    if failed_companies:
        print('------------')
        print('| FAILURES |')
        print('------------')
        for company, error, lineno in failed_companies:
            print(f'[FAIL company:{company}]')
            print(error)
            print(lineno)
        print('[FAIL summary] failed to get data for:', [c[0] for c in failed_companies])


def post_process(lines):
    size_emoji = '😃'
    # size_mapping = {
    #     '1 to 50 employees': size_emoji,
    #     '51 to 200 employees': size_emoji * 2,
    #     '201 to 500 employees': size_emoji * 3,
    #     '501 to 1000 employees': size_emoji * 4,
    #     '1001 to 5000 employees': size_emoji * 5,
    #     '5001 to 10000 employees': size_emoji * 6,
    #     '10000+ employees': size_emoji * 7,
    # }
    type_mapping = {
        r'Company - Private': r'Private',
        r'Company - Public (\(\w+\))': r'Public \1'
    }

    output_lines = []
    headers = lines.pop(0)
    print(headers)
    if headers[5] != 'Part of':
        print(f'[FAIL ASSERT] headers[5] != "Part of"\n{headers[5]}')
    if headers[8] != 'Type':
        print(f'[FAIL ASSERT] headers[8] != "Type"\n{headers[8]}')

    del headers[5]
    output_lines.append(headers)

    for split in lines:
        part_of = split.pop(5)
        if part_of != 'Unknown':
            if split[7] != 'Subsidiary or Business Segment':
                print(f'[FAIL ASSERT] split[7] != "Subsidiary or Business Segment"\n{line}')
            split[7] = f'Subsidiary of {part_of}'
        elif split[7] == 'Subsidiary or Business Segment':
            split[7] = 'Subsidiary'

        output_line = '\t'.join(split)
        # for k, v in size_mapping.items():
        #     if k in output_line:
        #         output_line = output_line.replace(k, f'{v} {k}')
        #         break

        for k, v in type_mapping.items():
            output_line = re.sub(k, v, output_line)

        output_lines.append(output_line.split('\t'))
    return output_lines


def get_intern_supply(use_cache=True):
    if use_cache:
        with open('intern_supply.html') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    else:
        r = requests.get('https://intern.supply/')
        soup = BeautifulSoup(r.text, 'html.parser')
        write_soup('intern_supply.html', soup)

    for p in soup.select('div.company-row p.title'):
        print(p.text.strip())

    # company_rows = soup.find_all('div', class_='company-row')
    # for row in company_rows:
    #     title = row.find('p', class_='title').text.strip()
    #     print(title)


if __name__ == '__main__':
    with open('companies_input.txt') as f:
        companies = [l.strip() for l in f.readlines()]
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--use-cache', action='store_true')
    parser.add_argument('-n', '--n-companies', type=int, default=2147483647)
    args = parser.parse_args()

    # get_intern_supply()
    # companies = ['Lyft']
    # companies = ['A9', 'Akuna Capital', 'American Express', 'Beme', 'Bloomberg', 'Cisco', 'Cofense (PhishMe)', 'Cogo', 'Couple', 'DE Shaw', 'Drive.ai', 'DriveTime', 'Ebay', 'Fidelity', 'Flatiron', 'Github', 'HomeAway', 'Hp', 'Hubspot', 'Icims', 'Ideo', 'Industry Drive', 'Intel', 'JPMorgan',
    #              'Juniper', 'Kayak', 'LastPass', 'MailChimp', 'Medium', 'NextCapital', 'Nvidia', 'Occipital', 'Palantir', 'Pandora', 'Playstation', 'Priceline', 'Quora', 'RedHat', 'Sensus', 'Sift Science', 'StateFarm', 'Tableau', 'Usaa', 'Valve', 'Vizio', 'Walt Disney', 'Zappos', 'Zurb']
    # companies = ['AppDynamics']
    output_data, failed_companies = scrape_companies_data(
        companies=companies, use_cache=args.use_cache, n=args.n_companies,
    )
    write_to_tsv_output(output_data, filename='companies_output_raw.tsv')
    write_to_tsv_output(post_process(output_data), filename='companies_output_post.tsv')
    print_failed_companies(failed_companies)
