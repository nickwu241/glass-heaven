#!/bin/sh
set -e
npm run build --prefix frontend
rm -rf backend/dist
mv frontend/dist backend/dist