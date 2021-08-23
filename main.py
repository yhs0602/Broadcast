# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket

import netifaces
import requests

SMS_PORT = 6543
UDP_PORT = 6542


def get_address():
    ifs = netifaces.interfaces()
    addrs = netifaces.ifaddresses('en0')
    ip = addrs[netifaces.AF_INET][0]['broadcast']
    print("Broadcasting to :", ip)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    # sock.bind((ip, 0))
    sock.sendto(b"pingping", (ip, UDP_PORT))
    try:
        data, address = sock.recvfrom(16)
        # print(address)
        sock.close()
        return address
    except socket.timeout:
        return None


# Press the green button in the gutter to run the script.
def send_sms(address, number, content):
    r = requests.get(url=f"http://{address}:{SMS_PORT}/sms", params={"number": number, "content": content})
    print(r.status_code)
    return r.status_code


if __name__ == '__main__':
    address = None
    while True:
        if address is None:
            address = get_address()
            if address is None:
                print("Failed to get server address")
                c = input("Continue?Y/N")
                if c == "Y" or c == "y":
                    continue
                else:
                    break
        print(f"Connected to {address[0]}:{address[1]}")
        number = input("Phone number")
        content = input("Content")
        c = input(f"Phone: {number}, content: {content}, continue?")
        if c == "Y" or c == "y":
            send_sms(address[0], number, content)
        else:
            print("Canceled.")
