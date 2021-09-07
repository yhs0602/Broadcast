# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import subprocess
import threading

import netifaces
import requests

SMS_PORT = 6543
UDP_PORT = 6542
SMS_RECEIVE_PORT = 6544


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


def rec_UDP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', SMS_RECEIVE_PORT))
    while True:
        # UDP commands for listening
        data, addr = sock.recvfrom(1024)
        print(f"Something came from {addr}")
        notify("Message", data)


CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''


def notify(title, text):
    subprocess.call(['osascript', '-e', CMD, title, text])


# Press the green button in the gutter to run the script.
def send_sms(address, number, content):
    r = requests.get(url=f"http://{address}:{SMS_PORT}/sms", params={"number": number, "content": content})
    print(r.status_code)
    return r.status_code


if __name__ == '__main__':
    address = None
    listen_UDP = threading.Thread(target=rec_UDP)
    listen_UDP.start()

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
            else:
                print(f"Connected to {address[0]}:{address[1]}")
                regurl = f"http://{address[0]}:{SMS_PORT}/register"
                r = requests.get(url=regurl)
                print(f"Registered to {regurl}; status code {r.status_code}")
        number = input("Phone number")
        content = input("Content")
        c = input(f"Phone: {number}, content: {content}, continue?")
        if c == "Y" or c == "y":
            send_sms(address[0], number, content)
        else:
            print("Canceled.")
