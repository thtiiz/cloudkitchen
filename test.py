import network
from utime import sleep_ms
import usocket as socket


# Setup WiFi connection:
def connect_wifi(ssid, passwd):
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    print("Connecting to WiFi '%s'. This takes some time..." % ssid)

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, passwd)

    while wifi.status() == network.STAT_CONNECTING:
        sleep_ms(100)

    if wifi.isconnected():
        print("Connection established. My IP is " + str(wifi.ifconfig()[0]))
        return True
    else:
        status = wifi.status()
        if status == network.STAT_WRONG_PASSWORD:
            status = "WRONG PASSWORD"
        elif status == network.STAT_NO_AP_FOUND:
            status = "NETWORK '%s' NOT FOUND" % ssid
        else:
            status = "Status code %d" % status
        print("Connection failed: %s!" % status)
        return False


# Echo Server:
def server(port, max_clients=1):
    print("Starting server at port %d..." % port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(max_clients)

    print("Echo-Server started. Connect a client now!")

    conn, cl_addr = sock.accept()
    print("New connection from %s:%d" % cl_addr)

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print("Received from client: " + str(data))
        conn.send(data.encode())

    sock.close()
    print("Server stopped.")


# Simple Client:
def client(host, port):
    print("Connecting to server %s:%d..." % (host, port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    print("Connection established.")
    print("Enter 'exit' to close the client.")

    while True:
        msg = input(">> ")
        if msg.lower().strip() == "exit":
            break

        sock.send(msg.encode())
        data = sock.recv(1024).decode()

        print("Received from server: %s" % data)

    sock.close()
    print("Client closed.")


# Prints available WiFi networks:
def print_wlan_list(sort_by=3, sort_desc=True):
    """sort by 0 = network name, 1 = bssid, 2 = ch, 3 = signal, ..."""

    from ubinascii import hexlify

    wlan = network.WLAN(network.STA_IF)
    prev_wlan_state = wlan.active()  # restore after scan
    wlan.active(True)

    table_header = ("network name", "BSSID", "CH", "signal", "authmode", "visibility")

    # safe all networks as tuples in a list, where [0] is a list
    # containing the maximum lengths of the subitems for oled;
    # - 0: network name
    # - 1: bssid (hardware address)
    # - 2: channel
    # - 3: rssi (signal strength, the higher the better)
    # - 4: authmode (most likely WPA/WPA2-PSK)
    # - 5: visible/hidden
    scan = [[0] * len(table_header)]

    # minimum length is table header
    for i in range(len(table_header)):
        scan[0][i] = len(table_header[i])

    # scan
    for item in wlan.scan():
        bssid = hexlify(item[1]).decode("ascii")
        bssid = ':'.join([bssid[i:i + 2] for i in range(0, len(bssid), 2)])

        new = (item[0].decode("utf-8"),
               bssid,
               item[2],
               item[3],
               ("open", "WEP", "WPA-PSK", "WPA2-PSK", "WPA/WPA2-PSK")[int(item[4])],
               ("visible", "hidden")[int(item[5])])
        scan.append(new)

        for i in range(0, len(scan[0])):
            len_new = len(str(new[i]))
            if len_new > scan[0][i]:
                scan[0][i] = len_new

    wlan.active(prev_wlan_state)

    # print table
    def center_subitems(ituple):
        retlist = []
        for i in range(len(ituple)):
            missing_spaces = scan[0][i] - len(str(ituple[i]))
            if missing_spaces > 0:
                spaces_right = int(missing_spaces / 2)
                spaces_left = missing_spaces - spaces_right
                retlist.append(' ' * spaces_left + str(ituple[i]) + ' ' * spaces_right)
            else:
                retlist.append(ituple[i])
        return tuple(retlist)

    header_string = "|| %s || %s | %s | %s | %s | %s ||" % center_subitems(table_header)
    print('-' * len(header_string))
    print(header_string)
    print('-' * len(header_string))

    for item in sorted(scan[1:], key=lambda x: x[sort_by], reverse=sort_desc):
        print("|| %s || %s | %s | %s | %s | %s ||" % center_subitems(item))

    print('-' * len(header_string))


# Interface for setting up server/client:
def main():
    while True:
        print()
        ssid = input("Enter your WiFi name: ")
        passwd = input("Enter WiFi password: ")
        if connect_wifi(ssid, passwd):
            break
        print("Scanning for available WiFi networks...")
        print_wlan_list()

    while True:
        cmd = input("Run server (S) or client (C)? ").lower()
        if cmd == 's':
            server(5678)
            break
        elif cmd == 'c':
            ip = input("Enter the server's IP address (see other ESP): ")
            try:
                client(ip, 5678)
                break
            except OSError:
                print("Connection failed. Did you already start the server on the other ESP?")
        else:
            print("Invalid input. Please enter 'S' or 'C'.")


main()