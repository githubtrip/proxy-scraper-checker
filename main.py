#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from different sources and save them to a file.
"""
from threading import Thread

from requests import get

from config import IP_SERVICE, SOURCES, TIMEOUT


def check(proxy: str) -> None:
    """Check proxy validity."""
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
            working_proxies.append(f"{proxy}\n")


def scrape(source: str) -> None:
    """Get HTTP proxies from source and check() their validity."""
    print(f"Getting {source}")
    try:
        req = get(source, timeout=30)
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


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = get(IP_SERVICE).text.strip()
    if isinstance(SOURCES, str):
        SOURCES = (SOURCES,)

    all_proxies = []
    threads = [
        Thread(target=scrape, args=(source.strip(),))
        for source in tuple(set(SOURCES))
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("Checking proxies...")
    working_proxies = []
    threads = [
        Thread(target=check, args=(proxy,))
        for proxy in tuple(set(all_proxies))
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with open("http_proxies.txt", "w") as f:
        f.writelines(working_proxies)
    print(
        """
Working proxies have been saved to http_proxies.txt
Thank you for using this script :)"""
    )
