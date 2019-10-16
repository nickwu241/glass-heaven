#!/usr/bin/env python

from operator import itemgetter

import requests
from flask import (Flask, abort, jsonify, render_template, request,
                   send_from_directory)
from flask_cors import CORS

import companies
import transformers
from init_firestore import companies_collection, db, get_docs


app = Flask(__name__, static_folder='dist/static')
CORS(app)

LOAD_COMPANIES_FUNCTION_URL = 'https://us-central1-easy-companies-overview.cloudfunctions.net/loadCompanies'


@app.route('/')
def index():
    return send_from_directory('./dist/', 'index.html')


@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory('./dist/', path)


@app.route('/companies', methods=['GET', 'POST'])
def companies_endpoint():
    if request.method == 'GET':
        return jsonify([doc.to_dict() for doc in companies_collection.stream()])
    elif request.method == 'POST':
        body = request.get_json(force=True)
        if not body.get('companies'):
            return jsonify([doc.to_dict() for doc in companies_collection.stream()])

        input_companies = [c.strip() for c in body['companies'].split(',') if c.strip()]
        skip_companies = set()
        # for company in input_companies:
        #     company_id = company.lower()
        #     if companies_collection.document(company_id).get().exists:
        #         skip_companies.add(company)

        output_data, failed_companies = companies.scrape_companies_data(
            input_companies, skip_companies=skip_companies)

        companies.print_failed_companies_errors(failed_companies)
        transformers.post_process(output_data)
        output = [company.as_dict for company in output_data]
        output += get_docs(skip_companies)
        output.sort(key=itemgetter('name'))
        requests.post(LOAD_COMPANIES_FUNCTION_URL, json=output)
        return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
