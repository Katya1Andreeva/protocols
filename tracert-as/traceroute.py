import argparse
import socket
import struct
import re
import subprocess
import ipwhois.exceptions
from ipwhois import IPWhois


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
    ip = socket.gethostbyname(socket.gethostname())
    netmask = socket.inet_ntoa(
        struct.pack('>I', (0xffffffff << (32 - 24)) & 0xffffffff))
    ip_binary = struct.unpack('>I', socket.inet_aton(ip))[0]
    netmask_binary = struct.unpack('>I', socket.inet_aton(netmask))[0]
    address_binary = struct.unpack('>I', socket.inet_aton(address))[0]
    return (ip_binary & netmask_binary) == (address_binary & netmask_binary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip")
    args = parser.parse_args()

    tracing(args.ip)
