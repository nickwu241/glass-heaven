#!/usr/bin/env python

from companies import scrape_companies_data, post_process, print_failed_companies
from init_firestore import db, companies_collection, get_docs

from flask import Flask, abort, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import requests


app = Flask(__name__, static_folder='dist/static')
CORS(app)

LOAD_COMPANIES_FUNCTION_URL = 'https://us-central1-easy-companies-overview.cloudfunctions.net/loadCompanies'


@app.route('/')
def index(path):
    return 'Hello World'


@app.route('/companies', methods=['GET', 'POST'])
def companies():
    if request.method == 'GET':
        return jsonify([doc.to_dict() for doc in companies_collection.stream()])
    elif request.method == 'POST':
        body = request.get_json(force=True)
        if not body.get('companies'):
            return jsonify([doc.to_dict() for doc in companies_collection.stream()])

        input_companies = [c.strip() for c in body['companies'].split(',') if c.strip()]
        skip_companies = set()
        for company in input_companies:
            company_id = company.lower()
            print(company)
            if companies_collection.document(company_id).get().exists:
                skip_companies.add(company)

        output_data, failed_companies = scrape_companies_data(input_companies, skip_companies=skip_companies)
        print_failed_companies(failed_companies)

        post_processed_data = post_process(output_data)

        requests.post(LOAD_COMPANIES_FUNCTION_URL, json=post_processed_data)

        post_processed_data_iter = iter(post_processed_data)
        headers = next(post_processed_data_iter)
        output = []
        for row in post_processed_data_iter:
            company_data = dict(zip(headers, row))
            output.append(company_data)

        output += get_docs(skip_companies)
        return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
