# Glass Heaven

`Glass Heaven` is a Web App that concisely shows you company ratings and overview so you don't need to keep on clicking on glassdoor links to find the information you need!

- Get overviews using your own list of companies or,
- See which popular companies people are curious about!

[Check it out here]()
## Inspiration

Frustrated with clicking too much for such little data.

## What it does

Concisely show you company ratings and overview so you don't need to click 22 times and open 11 different tabs.

## How I built it

- Google Cloud Compute: Worker nodes for hosting the web server
- Google Firebase Firestore: Datastore for storing all the company information
- Google Cloud Function: Writes to the DB (Firestore), called by the Python Web Server
- Frontend: Vue.js (Nuxt.js), custom styling with Tailwind CSS
- Web Server: Python (Flask) with JSON APIs and data transformers
- Web Scraper: Python (BeautifulSoup, requests) called by the web server

### Picture Credits: [Destinations](https://undraw.co/)
