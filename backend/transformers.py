import re
from typing import List

from models import Company


def write_to_tsv_output(companies: List[Company], filename: str) -> None:
    headers = [
        'Name',
        'Rating',
        'Review Counts',
        'Website',
        'Headquarters',
        'Part of',
        'Size',
        'Founded',
        'Type',
        'Industry',
        'Revenue',
        'Competitors',
        'Logo URL',
        'Overview URL',
        'Reviews URL',
        'LinkedIn URL',
    ]
    tsv_lines = ['\t'.join(headers) + '\n']
    field_names = [header.replace(' ', '_').lower() for header in headers]
    for c in companies:
        # Use an empty string for fields with None values.
        line_data = [c[field] if c[field] else '' for field in field_names]
        tsv_lines.append('\t'.join(line_data) + '\n')

    with open(filename, 'w') as f:
        f.writelines(tsv_lines)
    print(f'[INFO] wrote data to {filename}')


def post_process(companies: List[Company]) -> None:
    # size_emoji = '😃'
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

    def transform_type(company: Company) -> None:
        part_of = company['part_of']
        if company['part_of']:
            company['type'] = f'Subsidiary of {part_of}'
        elif company['type'] == 'Subsidiary or Business Segment':
            company['type'] = 'Subsidiary'
        else:
            for k, v in type_mapping.items():
                company['type'] = re.sub(k, v, company['type'])

    def transform_website(company: Company) -> None:
        if not company['website'].startswith('http'):
            company['website'] = 'https://' + company['website']

    def transform_revenue(company: Company) -> None:
        if company['revenue'] == 'Unknown / Non-Applicable':
            company['revenue'] = None

    for company in companies:
        transform_type(company)
        transform_website(company)
        transform_revenue(company)
