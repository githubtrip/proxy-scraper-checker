#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast and simple script to get and check free HTTP proxies
from proxyscrape.com and save them to a file
"""
from threading import Thread
from typing import Union

from requests import get

from config import IP_SERVICE, MY_IP, TIMEOUT


def check(
    proxy: str,
    my_ip: str,
    timeout: Union[float, None] = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Check proxy validity."""
    try:
        ip = get(
            ip_service,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=timeout,
        ).text
        if my_ip != ip:
            print(proxy)
            with open("http_proxies.txt", "a") as f:
                f.write(f"{proxy}\n")
    except Exception:
        pass


def get_proxies(
    my_ip: str,
    timeout: Union[float, None] = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Get HTTP proxies from proxyscrape.com and check() their validity."""
    try:
        req = get(
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http"
        )
        if req.status_code == 200:
            array = req.text.replace("\r", "\n").split("\n")
            for proxy in array:
                if proxy:
                    Thread(
                        target=check,
                        args=(proxy.strip(), my_ip, timeout, ip_service),
                    ).start()
        else:
            print(req.text)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    if not MY_IP:
        MY_IP = get(IP_SERVICE).text.strip()
    open("http_proxies.txt", "w").close()
    get_proxies(MY_IP, TIMEOUT, IP_SERVICE)
