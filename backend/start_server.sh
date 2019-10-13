#!/bin/sh
gunicorn -w 2 -k eventlet -b 0.0.0.0:3000 --log-level DEBUG app:app -