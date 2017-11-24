from flask import request


def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    if isinstance(ip, str) and len(ip.split(",")) > 1:
        ip = ip.split(",")[0].replace(" ", "")
    return ip
