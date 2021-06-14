#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from different sources and save them to a file.
Supports getting geolocation info for proxies.
"""
from threading import Thread
from time import sleep

from maxminddb import open_database
from requests import get

from config import GEOLOCATION, IP_SERVICE, SOURCES, TIMEOUT


def scrape(source: str) -> None:
    """Get proxies from source and append them to all_proxies."""
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


def check(proxy: str) -> None:
    """Check proxy validity and append it to working_proxies."""
    try:
        ip = get(
            IP_SERVICE,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=TIMEOUT,
        ).text.strip()
    except Exception:
        pass
    else:
        if MY_IP != ip:
            if GEOLOCATION:
                geolocation = reader.get(ip)
                proxy += (
                    try_to_add_location(geolocation, "country")
                    + try_to_add_location(geolocation, "subdivisions")
                    + try_to_add_location(geolocation, "city")
                )
            working_proxies.append(proxy)


def try_to_add_location(geolocation: dict, first_key: str) -> str:
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


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = get(IP_SERVICE).text.strip()
    if isinstance(SOURCES, str):
        SOURCES = (SOURCES,)

    print("Getting SOURCES")
    all_proxies = []
    run_threads(
        [
            Thread(target=scrape, args=(source.strip(),))
            for source in tuple(set(SOURCES))
        ]
    )

    print(f"Checking {len(all_proxies)} proxies")
    if GEOLOCATION:
        reader = open_database("GeoLite2-City.mmdb")
    working_proxies = []
    run_threads(
        [
            Thread(
                target=check,
                args=(proxy.replace("http://", "").replace("https://", ""),),
            )
            for proxy in tuple(set(all_proxies))
        ]
    )

    with open("http_proxies.txt", "w", encoding="utf-8") as f:
        for proxy in sorted(working_proxies):
            f.write(f"{proxy}\n")
    print(
        """
Working proxies have been saved to http_proxies.txt
Thank you for using this script :)"""
    )
