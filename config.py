# Service for getting your IP address and checking if proxies are valid.
IP_SERVICE = "https://ident.me"

# Your IP address.
# Leave empty to get it from IP_SERVICE.
MY_IP = ""

# How many seconds to wait for the client to make a connection?
# Lower value results in getting less proxies but they're going to be faster.
# I set this value to 1 or 1.5.
# If set to None the request will continue until the connection is closed.
TIMEOUT = 1.5
