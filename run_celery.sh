#!/usr/bin/env bash
export FLASK_SITE_SETTINGS='../dev_settings.py'
celery -A kman_site.application:celery worker -B
