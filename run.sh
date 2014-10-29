#!/usr/bin/env bash
export KMAN_WEB_SETTINGS='../dev_settings.py'
gunicorn --log-level debug --log-file "-" -k gevent -b 127.0.0.1:5000 kman_web.application:app
