# -*- coding: utf-8 -*-

# Where to get the proxy lists from.
SOURCES = [
    # "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&country=US&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]

# Service for getting your IP address and checking if proxies are valid.
IP_SERVICE = "https://ident.me"

# How many seconds to wait for the client to make a connection.
# Lower value results in getting less proxies but they're going to be faster.
# If set to None the request will continue until the connection is closed.
TIMEOUT = 3
