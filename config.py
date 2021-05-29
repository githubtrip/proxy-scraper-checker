# -*- coding: utf-8 -*-

# Service for getting your IP address and checking if proxies are valid.
IP_SERVICE = "https://ident.me"

# Your IP address.
# Leave empty to get it from IP_SERVICE.
MY_IP = ""

# List of country codes.
# See possible values at https://proxyscrape.com/free-proxy-list
# COUNTRY_CODES = ["US", "RU"]
COUNTRY_CODES = ["all"]

# Possible values are all, yes and no
# SSL = ["yes", "no"]
SSL = ["all"]

# List of proxy anonymity levels.
# Possible values are all, elite, anonymous and transparent
# ANONYMITY_LEVELS = ["elite", "anonymous"]
ANONYMITY_LEVELS = ["all"]

# How many seconds to wait for the client to make a connection.
# Lower value results in getting less proxies but they're going to be faster.
# I set this value to 1 or 1.5.
# If set to None the request will continue until the connection is closed.
TIMEOUT = 3
