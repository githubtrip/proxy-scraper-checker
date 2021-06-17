#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread
from time import sleep

from maxminddb import open_database
from requests import get

from config import (
    ANONYMOUS_ONLY,
    GEOLOCATION,
    HTTP,
    HTTP_SOURCES,
    IP_SERVICE,
    SOCKS4,
    SOCKS4_SOURCES,
    SOCKS5,
    SOCKS5_SOURCES,
    TIMEOUT,
)


def scrape(source: str, all_proxies: list) -> None:
    """Get proxies from source and append them to all_proxies.

    Args:
        source (str): where to download proxy list from.
        all_proxies (list): a list in which all proxies are written.
    """
    try:
        req = get(source, timeout=15)
    except Exception as e:
        print(f"ERROR {source}: {e}")
    else:
        status_code = req.status_code
        if status_code == 200:
            for proxy in req.text.splitlines():
                proxy = proxy.strip()
                if proxy:
                    all_proxies.append(proxy)
        else:
            print(f"ERROR {source} status code: {status_code}")


def check(proxy: str, protocol: str, working_proxies: list) -> None:
    """Check proxy validity and append it to working_proxies.

    Args:
        proxy (str): ip:port.
        protocol (str): http/socks4/socks5.
        working_proxies (list): a list that is subsequently written to a file.
    """
    try:
        ip = get(
            IP_SERVICE,
            proxies={
                "http": f"{protocol}://{proxy}",
                "https": f"{protocol}://{proxy}",
            },
            timeout=TIMEOUT,
        ).text.strip()
    except Exception:
        pass
    else:
        if MY_IP != ip:
            if ANONYMOUS_ONLY:
                if ip != proxy.split(":")[0]:
                    if GEOLOCATION:
                        proxy += get_geolocation(ip)
                    working_proxies.append(proxy)
            else:
                if GEOLOCATION:
                    proxy += get_geolocation(ip)
                working_proxies.append(proxy)


def get_geolocation(ip: str) -> str:
    """Get proxy's geolocation.

    Args:
        ip (str): proxy ip.

    Returns:
        str: proxy's geolocation.
    """
    geolocation = reader.get(ip)
    return (
        try_to_add_location(geolocation, "country")
        + try_to_add_location(geolocation, "subdivisions")
        + try_to_add_location(geolocation, "city")
    )


def try_to_add_location(geolocation: dict, first_key: str) -> str:
    """Tries to get name of country, subdivision or city.

    Args:
        geolocation (dict): dictionary with geolocation info.
        first_key (str): country, subdivision or city.

    Returns:
        str: name of country, subdivision or city.
    """
    try:
        geolocation = geolocation[first_key]
    except KeyError:
        return "::None"
    try:
        return f"::{geolocation['names']['en']}"
    except TypeError:
        return f"::{geolocation[0]['names']['en']}"


def run_threads(threads: list) -> None:
    for t in threads:
        try:
            t.start()
        except RuntimeError:
            sleep(TIMEOUT)
            t.start()
    for t in threads:
        t.join()


def run_scraper(sources: tuple, protocol: str) -> None:
    """Runs scraping and checking certain protocol proxies.

    Args:
        sources (tuple): where to get proxies from.
        protocol (str): http/socks4/socks5.
    """
    if isinstance(sources, str):
        sources = (sources,)
    print(f"Getting {protocol.upper()}_SOURCES")
    all_proxies = []
    run_threads(
        [
            Thread(target=scrape, args=(source.strip(), all_proxies))
            for source in tuple(set(sources))
        ]
    )
    print(f"Checking {len(all_proxies)} {protocol} proxies")
    working_proxies = []
    run_threads(
        [
            Thread(
                target=check,
                args=(
                    proxy.replace(f"{protocol}://", "").replace(
                        "https://", ""
                    ),
                    protocol,
                    working_proxies,
                ),
            )
            for proxy in tuple(set(all_proxies))
        ]
    )

    with open(f"{protocol}_proxies.txt", "w", encoding="utf-8") as f:
        for proxy in sorted(working_proxies):
            f.write(f"{proxy}\n")


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = get(IP_SERVICE).text.strip()
    if GEOLOCATION:
        reader = open_database("GeoLite2-City.mmdb")
    if HTTP:
        run_scraper(HTTP_SOURCES, "http")
    if SOCKS4:
        run_scraper(SOCKS4_SOURCES, "socks4")
    if SOCKS5:
        run_scraper(SOCKS5_SOURCES, "socks5")
