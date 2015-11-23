#!/usr/bin/env bash
export KMAD_WEB_SETTINGS='../dev_settings.py'
celery -A kmad_web.application:celery worker -B -n kmad_web.%h
