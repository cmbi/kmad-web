from ipwhois.ipwhois import IPWhois
import sys


def invert_dict(d):
    return {d[k]: k for k in d}


def get_ip_data(ip_address):
    save_stderr = sys.stderr
    sys.stderr = open('trash', 'w')
    ipw = IPWhois(ip_address)
    ipw_lookup = ipw.lookup_whois()["nets"][0]
    sys.stderr = save_stderr
    data_txt = log_data(ipw_lookup)
    return data_txt


def log_data(ipw_lookup):
    log_txt = "desc:" + str(ipw_lookup["description"]) + "city:" + \
        str(ipw_lookup["city"]) + "country:" + str(ipw_lookup["country"])
    log_txt = log_txt.replace("\n", "")
    return log_txt
