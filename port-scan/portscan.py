import argparse
import socket
import threading


def scan_tcp_port(ip, port):
    service = ''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((ip, port))
    if result == 0:
        try:
            service = socket.getservbyport(port, 'tcp')
        except:
            pass
    print('TCP', port, service)

    sock.close()


def scan_udp_port(ip, port):
    service = ''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.sendto(b'ping', (ip, port))
            data, _ = sock.recvfrom(1024)
            service = socket.getservbyport(port, 'udp')
        except:
            pass
    print('UDP', port, service)


def scan_tcp(host, start_port, end_port):

    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_tcp_port, args=(host, port))
        t.start()


def scan_udp(host, start_port, end_port):
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_udp_port, args=(host, port))
        t.start()


def scaned(host, start_port, end_port, tcp, udp):
    try:
        ip = socket.gethostbyname(host)
    except socket.error:
        print("You should check the host, it's not correct")
        return
    if not tcp and not udp:
        print("Please specify scan type")

    if tcp:
        scan_tcp(ip, start_port, end_port)
    if udp:
        scan_udp(ip, start_port, end_port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host",
                        type=str,
                        help=" host address whose ports are checked")
    parser.add_argument("-t", action="store_true", help="scan TCP ports")
    parser.add_argument("-u", action="store_true", help="scan UDP ports")
    parser.add_argument("-p", "--ports",
                        type=int,
                        help="port scan range",
                        default=[1, 65535], nargs=2)
    args = parser.parse_args()
    scaned(args.host, args.ports[0], args.ports[1], args.t, args.u)