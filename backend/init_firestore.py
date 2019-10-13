import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

project_id = 'easy-companies-overview'
cred = credentials.Certificate('easy-companies-overview-firebase-adminsdk-7idn2-520e664df3.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
companies_collection = db.collection('companies')


def get_docs(companies):
    return [companies_collection.document(c.lower()).get().to_dict() for c in companies]
