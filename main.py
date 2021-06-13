#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from different sources and save them to a file.
Supports getting geolocation info for proxies.
"""
from json import loads
from threading import Thread
from time import sleep

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
            working_proxies.append(proxy)


def geolocation(proxy: str) -> None:
    """Get proxy's geolocation."""
    try:
        geolocation = loads(
            get(
                f"https://geolocation-db.com/jsonp/{proxy.split(':')[0]}",
                timeout=15,
            )
            .text.split("(")[1]
            .strip(")")
        )
    except Exception:
        country_name = None
        city = None
        state = None
    else:
        country_name = geolocation["country_name"]
        if country_name == "Not found":
            country_name = None
        city = geolocation["city"]
        if city == "Not found":
            city = None
        state = geolocation["state"]
        if state == "Not found":
            state = None
    proxies_geolocation.append(f"{proxy}::{country_name}::{city}::{state}")


def run_threads(threads: list) -> None:
    for t in threads:
        try:
            t.start()
        except RuntimeError:
            sleep(TIMEOUT)
            t.start()
    for t in threads:
        t.join()


def save_proxies(proxies: list) -> None:
    with open("http_proxies.txt", "w", encoding="utf-8") as f:
        for proxy in sorted(proxies):
            f.write(f"{proxy}\n")


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = get(IP_SERVICE).text.strip()
    if isinstance(SOURCES, str):
        SOURCES = (SOURCES,)

    print("Getting SOURCES")
    all_proxies = []
    threads = [
        Thread(target=scrape, args=(source.strip(),))
        for source in tuple(set(SOURCES))
    ]
    run_threads(threads)

    print(f"Checking {len(all_proxies)} proxies")
    working_proxies = []
    threads = [
        Thread(
            target=check,
            args=(proxy.replace("http://", "").replace("https://", ""),),
        )
        for proxy in tuple(set(all_proxies))
    ]
    run_threads(threads)

    if GEOLOCATION:
        print(f"Getting geolocation for {len(working_proxies)} proxies")
        proxies_geolocation = []
        threads = [
            Thread(target=geolocation, args=(proxy,))
            for proxy in working_proxies
        ]
        run_threads(threads)
        save_proxies(proxies_geolocation)
    else:
        save_proxies(working_proxies)

    print(
        """
Working proxies have been saved to http_proxies.txt
Thank you for using this script :)"""
    )
