#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from proxyscrape.com and save them to files.
"""
from threading import Thread
from typing import Union

from requests import get

from config import (
    ANONYMITY_LEVELS,
    COUNTRY_CODES,
    IP_SERVICE,
    MY_IP,
    SSL,
    TIMEOUT,
)


def check(
    proxy: str,
    my_ip: str,
    country: str = "all",
    ssl: str = "all",
    anonymity: str = "all",
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
            with open(f"http_{country}_{ssl}_{anonymity}.txt", "a") as f:
                f.write(f"{proxy}\n")
    except Exception:
        pass


def get_proxies(
    my_ip: str,
    country: str = "all",
    ssl: str = "all",
    anonymity: str = "all",
    timeout: Union[float, None] = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Get HTTP proxies from proxyscrape.com and check() their validity."""
    try:
        req = get(
            f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&country={country}&ssl={ssl}&anonymity={anonymity}"
        )
        if req.status_code == 200:
            array = req.text.replace("\r", "\n").split("\n")
            open(f"http_{country}_{ssl}_{anonymity}.txt", "w").close()
            for proxy in array:
                if proxy:
                    Thread(
                        target=check,
                        args=(
                            proxy.strip(),
                            my_ip,
                            country,
                            ssl,
                            anonymity,
                            timeout,
                            ip_service,
                        ),
                    ).start()
        else:
            print(
                f"Couldn't get country={country}, ssl={ssl}, anonymity={anonymity}:\n{req}\n{req.text}"
            )
    except Exception as e:
        print(
            f"Couldn't get country={country}, ssl={ssl}, anonymity={anonymity}.\nException: {e}"
        )


if __name__ == "__main__":
    if not MY_IP:
        MY_IP = get(IP_SERVICE).text.strip()
    for country_code in COUNTRY_CODES:
        country_code = (
            "all"
            if country_code.strip().lower() == "all"
            else country_code.strip().upper()
        )
        for ssl in SSL:
            for anonymity_level in ANONYMITY_LEVELS:
                Thread(
                    target=get_proxies,
                    args=(
                        MY_IP,
                        country_code,
                        ssl.strip().lower(),
                        anonymity_level.strip().lower(),
                        TIMEOUT,
                        IP_SERVICE.strip(),
                    ),
                ).start()
