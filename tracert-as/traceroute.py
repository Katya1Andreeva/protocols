import argparse
import socket
import struct
import re
import subprocess

from ipwhois import IPWhois, ipwhois


def tracing(host):
    traceroute = subprocess.Popen(["tracert", '-d', host],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
    visited_ip = []
    for line in iter(traceroute.stdout.readline, b''):
        visited_ip.append(line.decode('866'))
    traceroute.stdout.close()

    result = []
    for line in visited_ip:
        ip = re.search(re.compile(r'(\d{1,3}\.){3}\d{1,3}'), line)
        if ip is not None:
            if is_local_address(ip.group(0)):
                result.append((ip.group(0), ["local"]))
            else:
                information = whois(ip.group(0))
                result.append((ip.group(0), information))
                print_node(result)

    return result


def whois(address):
    if address == '*':
        return '-'
    try:
        result = IPWhois(address)
    except ipwhois.exceptions.IPDefinedError:
        return '-'

    need = result.lookup_whois()
    network_information = []
    if need['nets'][0]['name'] is not None:
        network_information.append(need['nets'][0]['name'])
    if need['asn'] is not None:
        network_information.append(need['asn'])
    if need['asn'] is not None:
        network_information.append(need['asn_country_code'])
    if len(network_information) == 0:
        network_information.append("-")
    """network_information = [need['nets'][0]['name'],
                           need['asn'],
                           need['asn_country_code']]"""

    return network_information


def print_node(result):
    i = len(result)
    print(f"{i}.  {result[i - 1][0]}")
    print(f"{' '.join(result[i - 1][1])}\n")


def is_local_address(address):
    segments = [int(x) for x in address.split('.')]

    # 10.0.0.0 — 10.255.255.255
    if segments[0] == 10:
        return True
    # 192.168.0.0 — 192.168.255.255
    if segments[0] == 192 and segments[1] == 168:
        return True
    # 100.64.0.0 — 100.127.255.255
    if segments[0] == 100 and 127 >= segments[1] >= 64:
        return True
    # 172.16.0.0 — 172.31.255.255
    if segments[0] == 172 and 31 >= segments[1] >= 16:
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip")
    args = parser.parse_args()

    tracing(args.ip)
