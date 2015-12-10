#!/usr/bin/env bash
export KMAD_WEB_SETTINGS='../dev_settings.py'
gunicorn --log-level info --log-file "-" -k gevent -b 127.0.0.1:5000 kmad_web.application:app
