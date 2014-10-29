#!/usr/bin/env bash
export KMAN_WEB_SETTINGS='../dev_settings.py'
celery -A kman_web.application:celery worker -B
