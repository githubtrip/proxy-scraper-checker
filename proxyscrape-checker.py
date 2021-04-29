#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast and simple script to get and check free HTTP proxies
from proxyscrape.com and save them to a file
"""
from threading import Thread
from typing import Union

from requests import get


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
            with open("proxies.txt", "a") as f:
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
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"
        )
        if req.status_code == 200:
            array = req.text.replace("\r", "").split("\n")
            for proxy in array:
                if proxy:
                    Thread(
                        target=check, args=(proxy, my_ip, timeout, ip_service)
                    ).start()
        else:
            print(req.text)
    except Exception as e:
        print(e)


def main():
    ip_service = input(
        "Service to get your IP (leave empty to use https://ident.me): "
    )
    timeout = input(
        """\nHow many seconds to wait for the client to make a connection?
Lower value results in getting less proxies but they're going to be faster.
I personally set this value to 1 or 2.
Empty means that the request will continue until the connection is closed.
Timeout = """
    )
    if not ip_service:
        ip_service = "https://ident.me"
    my_ip = get(ip_service).text
    open("proxies.txt", "w").close()
    if timeout:
        get_proxies(my_ip, int(timeout), ip_service)
    else:
        get_proxies(my_ip, None, ip_service)


if __name__ == "__main__":
    main()
