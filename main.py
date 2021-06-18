#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config import (
    ANONYMOUS_ONLY,
    GEOLOCATION,
    HTTP,
    HTTP_SOURCES,
    IP_SERVICE,
    IPV4_ONLY,
    SOCKS4,
    SOCKS4_SOURCES,
    SOCKS5,
    SOCKS5_SOURCES,
    TIMEOUT,
)
from proxy_scraper_checker import ProxyScraperChecker


def main() -> None:
    """Create a class instance and run it."""
    client = ProxyScraperChecker(
        ANONYMOUS_ONLY,
        "GeoLite2-City.mmdb" if GEOLOCATION else "",
        HTTP_SOURCES if HTTP else (),
        IP_SERVICE,
        IPV4_ONLY,
        SOCKS4_SOURCES if SOCKS4 else (),
        SOCKS5_SOURCES if SOCKS5 else (),
        TIMEOUT,
    )
    client.main()


if __name__ == "__main__":
    main()
