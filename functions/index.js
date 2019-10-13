const functions = require("firebase-functions");

const Firestore = require("@google-cloud/firestore");
const PROJECTID = "easy-companies-overview";
const COLLECTION_NAME = "companies";
const firestore = new Firestore({
  projectId: PROJECTID
});

exports.loadCompanies = functions.https.onRequest(async (request, response) => {
  let companies = request.body;
  let headers = request.body[0];
  let promises = [];
  for (let i = 1; i < companies.length; i++) {
    let row = companies[i];
    let companyId = row[0].toLowerCase();
    let data = {};
    for (let j = 0; j < headers.length; j++) {
      data[headers[j]] = row[j];
    }
    promises.push(
      firestore
        .collection(COLLECTION_NAME)
        .doc(companyId)
        .set(data)
    );
  }
  return Promise.all(promises)
    .then(() => {
      return response.status(200).send("OK");
    })
    .catch(error => {
      console.log(error);
      return response.status(404).send(error);
    });
});
