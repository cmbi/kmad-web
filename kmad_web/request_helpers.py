import logging
import sys

from flask import request
from ipwhois.ipwhois import IPWhois

_log = logging.getLogger(__name__)


def log_data(ipw_lookup):
    log_txt = "desc:" + str(ipw_lookup["description"]) + "city:" + str(ipw_lookup["city"]) + \
        "country:" + str(ipw_lookup["country"])
    log_txt = log_txt.replace("\n", "")
    return log_txt

def get_ip_data(ip_address):
    save_stderr = sys.stderr
    sys.stderr = open('trash', 'w')
    ipw = IPWhois(ip_address)
    ipw_lookup = ipw.lookup_whois()["nets"][0]
    sys.stderr = save_stderr
    data_txt = log_data(ipw_lookup)
    return data_txt


def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    try:
        ip_log = get_ip_data(ip)
    except RuntimeError as e:
        logger.error("Retrieving IP data failed. Error:%s\n", e.message)
        ip_log = ip

    return ip
