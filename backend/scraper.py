import os
import re
from typing import Callable, Dict, Tuple

import requests
from bs4 import BeautifulSoup

CACHE_FOLDER = '.scrape-cache'
os.makedirs(CACHE_FOLDER, exist_ok=True)


def scrape(
        url: str,
        cached_filename: str,
        callback: Callable[[BeautifulSoup], any],
        use_cache: bool = False
) -> any:
    """Returns the value returned from the `callback` function passed."""
    if use_cache:
        soup = __read_soup_from_file(cached_filename)
    else:
        soup = __get_soup(url, cached_filename=cached_filename)
    return callback(soup)


def get_linkedin_url(
        company: str,
        linkedin_url_re: re.Pattern = re.compile(r'https://www.linkedin.com/company/\w+/')
) -> str:
    soup = __get_google_search_soup(f'{company}+linkedin')
    for a in soup.find_all('a'):
        url = a.get('href', '')
        match = linkedin_url_re.search(url)
        if match:
            return match.group(0)
    return None


def get_glassdoor_urls(company: str) -> Tuple[str, str]:
    """Returns the Glassdoor overview and reviews URLs respectively."""
    def find_links_from_a_elements(all_a):
        overview_url = reviews_url = None
        for a in all_a:
            if overview_url and reviews_url:
                break

            url = a.get('href', '')
            if ('glassdoor.com/' not in url and 'glassdoor.ca/' not in url):
                continue

            if not overview_url and 'Overview' in url or \
                    (a.find('div') and a.find('div').text.strip().startswith('Working at')):
                overview_url = url

            if not reviews_url and 'Reviews' in url and 'Employee-Review' not in url:
                reviews_url = url

        return overview_url, reviews_url

    soup = __get_google_search_soup(f'{company}+glassdor')
    overview_url, reviews_url = find_links_from_a_elements(soup.find_all('a'))
    if overview_url is None:
        soup = __get_google_search_soup(f'{company}+overview+glassdor')
        overview_url, _ = find_links_from_a_elements(soup.find_all('a'))
    if reviews_url is None:
        soup = __get_google_search_soup(f'{company}+reviews+glassdor')
        _, reviews_url = find_links_from_a_elements(soup.find_all('a'))

    if overview_url is None or reviews_url is None:
        raise Exception(f'Cannot find both URLs for "{company}": {overview_url} {reviews_url}')

    return overview_url, reviews_url


def get_overview_data(soup: BeautifulSoup) -> Dict[str, str]:
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


def get_reviews_data(soup: BeautifulSoup) -> Dict[str, str]:
    div = soup.find('div', id='EmpStats')
    review_counts = div.find('span', class_='count').text.strip()
    rating = div.find(
        'div', class_='common__EIReviewsRatingsStyles__ratingNum').text.strip()
    # Rating, Review Counts
    return {'rating': rating, 'review_counts': review_counts}


def print_intern_supply_companies(use_cache: bool = True) -> None:
    def print_companies(soup):
        for p in soup.select('div.company-row p.title'):
            print(p.text.strip())

    scrape('intern_supp.html', 'intern_supply.html', print_companies)


def __write_soup(filename: str, soup: BeautifulSoup):
    # errors='surrogatepass' for non UTF-8 characters: e.g. Salesforce
    filepath = os.path.join(CACHE_FOLDER, filename)
    with open(filepath, 'w', errors='surrogatepass') as f:
        f.write(str(soup))


def __read_soup_from_file(filename: str):
    filepath = os.path.join(CACHE_FOLDER, filename)
    with open(filepath) as f:
        return BeautifulSoup(f.read(), 'html.parser')
    raise ValueError(f'Error opening {filename} does not exist')


def __get_soup(url: str, cached_filename: str = None):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    }
    response = requests.get(url, headers=request_headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    if cached_filename:
        __write_soup(cached_filename, soup)
    return soup


def __get_google_search_soup(query: str) -> BeautifulSoup:
    query = query.replace(' ', '+')
    query_underscore_separated = query.replace('+', '_').lower()
    return __get_soup(
        f'https://www.google.com/search?q={query}',
        cached_filename=f'google_{query_underscore_separated}.html'
    )
