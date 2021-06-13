# -*- coding: utf-8 -*-

# Where to get the proxy lists from.
SOURCES = (
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/proxiesmaster/Free-Proxy-List/main/proxies.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt",
)

# Add geolocation info for each proxy. True or False.
# Output format is ip:port::country_name::city::state
GEOLOCATION = False

# Service for getting your IP address and checking if proxies are valid.
IP_SERVICE = "https://ident.me"

# How many seconds to wait for the client to make a connection.
# Lower value results in getting less proxies but they're going to be faster.
TIMEOUT = 3
