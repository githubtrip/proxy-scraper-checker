#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from different sources and save them to a file.
"""
from threading import Thread

from requests import get

from config import IP_SERVICE, SOURCES, TIMEOUT


def check(
    proxy: str,
    my_ip: str,
    timeout: float = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Check proxy validity."""
    try:
        ip = get(
            ip_service,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=timeout,
        ).text.strip()
    except Exception:
        pass
    else:
        if my_ip != ip:
            proxies.append(f"{ip}\n")


def get_proxies(
    source: str,
    my_ip: str,
    timeout: float = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Get HTTP proxies from source and check() their validity."""
    print(f"Checking {source}")
    try:
        req = get(source)
    except Exception as e:
        print(f"ERROR {source}: {e}")
    else:
        status_code = req.status_code
        if status_code == 200:
            proxies = req.text.replace("\r", "\n").split("\n")
            threads = []
            for proxy in proxies:
                proxy = proxy.strip()
                if proxy:
                    t = Thread(
                        target=check, args=(proxy, my_ip, timeout, ip_service)
                    )
                    threads.append(t)
                    t.start()
            for t in threads:
                t.join()
            print(f"Finished {source}")
        else:
            print(f"ERROR {source} status code: {status_code}")


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = get(IP_SERVICE).text.strip()
    proxies = []
    threads = []
    for source in SOURCES:
        t = Thread(
            target=get_proxies,
            args=(source.strip(), MY_IP, TIMEOUT, IP_SERVICE),
        )
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    with open("http_proxies.txt", "w") as f:
        f.writelines(list(set(proxies)))
