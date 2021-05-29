#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast, simple and configurable script to get and check free HTTP proxies
from proxyscrape.com and save them to files.
"""
from threading import Thread

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
            with open(f"http_{country}_{ssl}_{anonymity}.txt", "a") as f:
                f.write(f"{proxy}\n")


def get_proxies(
    my_ip: str,
    country: str = "all",
    ssl: str = "all",
    anonymity: str = "all",
    timeout: float = None,
    ip_service: str = "https://ident.me",
) -> None:
    """Get HTTP proxies from proxyscrape.com and check() their validity."""
    print(f"Checking country={country}, ssl={ssl}, anonymity={anonymity}...")
    try:
        req = get(
            f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&country={country}&ssl={ssl}&anonymity={anonymity}"
        )
    except Exception as e:
        print(
            f"""Couldn't get country={country}, ssl={ssl}, anonymity={anonymity}.
Exception: {e}"""
        )
    else:
        if req.status_code == 200:
            open(f"http_{country}_{ssl}_{anonymity}.txt", "w").close()
            proxies = req.text.replace("\r", "\n").split("\n")
            for proxy in proxies:
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
            print(
                f"Finished checking country={country}, ssl={ssl}, anonymity={anonymity}"
            )
        else:
            print(
                f"""Couldn't get country={country}, ssl={ssl}, anonymity={anonymity}:
{req}
{req.text}"""
            )


if __name__ == "__main__":
    IP_SERVICE = IP_SERVICE.strip()
    MY_IP = MY_IP.strip() if MY_IP else get(IP_SERVICE).text.strip()
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
                        IP_SERVICE,
                    ),
                ).start()
