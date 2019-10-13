#!/usr/bin/env python
import csv
from init_firestore import db

SHOULD_SKIP_EXISTS = False

with open('companies_output_post.tsv') as tsvfile:
    reader = csv.reader(tsvfile, delimiter='\t')
    headers = next(reader)
    for row in reader:
        company_id = row[0].lower()
        company_data = dict(zip(headers, row))

        doc_ref = db.collection('companies').document(company_id)
        if SHOULD_SKIP_EXISTS and doc_ref.get().exists:
            print(f'[SKIP] {company_id}')
        else:
            doc_ref.set(company_data)
            print(f'[WRITE] {company_id}')
