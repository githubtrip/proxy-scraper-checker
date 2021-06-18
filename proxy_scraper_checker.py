# -*- coding: utf-8 -*-
from ipaddress import IPv4Address
from threading import Thread
from time import sleep
from typing import Union

from maxminddb import open_database
from requests import get


class ProxyScraperChecker(object):
    def __init__(
        self,
        anonymous_only: bool = False,
        geolocation_mmdb: str = "",
        http_sources: Union[tuple, str] = (),
        ip_service: str = "https://ident.me",
        ipv4_only: bool = False,
        socks4_sources: Union[tuple, str] = (),
        socks5_sources: Union[tuple, str] = (),
        timeout: int = 5,
    ) -> None:
        """Scrape and check proxies from sources and save them to a file.

        Args:
            anonymous_only (bool): Save only anonymous proxies.
                Defaults to False.
            geolocation_db (str): Path to the geolocation mmdb if you want to
                add location info for each proxy.
                Output format is ip:port::Country Name::State::City.
                Defaults to "".
            http_sources (Union[tuple, str]): http proxy lists sources.
                Defaults to ().
            ip_service (str): Service for getting your IP address
                and checking if proxies are valid.
                Defaults to "https://ident.me".
            ipv4_only (bool): Save only IPv4 proxies.
                Defaults to False.
            socks4_sources (Union[tuple, str]): socks4 proxies lists sources.
                Defaults to ().
            socks5_sources (Union[tuple, str]): socks5 proxies lists sources.
                Defaults to ().
            timeout (int): How many seconds to wait for the connection.
                Defaults to 5.
        """
        self.IP_SERVICE = ip_service.strip()
        self.MY_IP = get(self.IP_SERVICE).text.strip()
        self.ANONYMOUS_ONLY = anonymous_only
        self.IPV4_ONLY = ipv4_only
        self.HTTP_SOURCES = self.prepare_sources(http_sources)
        self.SOCKS4_SOURCES = self.prepare_sources(socks4_sources)
        self.SOCKS5_SOURCES = self.prepare_sources(socks5_sources)
        self.TIMEOUT = timeout
        self.GEOLOCATION_MMDB = geolocation_mmdb
        if self.GEOLOCATION_MMDB:
            self.READER = open_database(self.GEOLOCATION_MMDB)

    @staticmethod
    def prepare_sources(sources: Union[tuple, str]) -> tuple:
        """Remove duplicate sources or convert str to tuple.

        Args:
            sources (Union[tuple, str]): Proxy sources.

        Returns:
            tuple: Sources without duplicates.
        """
        return (sources,) if isinstance(sources, str) else tuple(set(sources))

    @staticmethod
    def start_threads(threads: list) -> None:
        """Start and join threads.

        Args:
            threads (list): Threads to be started and joined.
        """
        for t in threads:
            try:
                t.start()
            except RuntimeError:
                sleep(TIMEOUT)
                t.start()
        for t in threads:
            t.join()

    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """Check if ip is IPv4.

        Args:
            ip (str): IP address.

        Returns:
            bool: Return True if ip is IPv4.
        """
        try:
            if IPv4Address(ip):
                return True
        except Exception:
            pass
        return False

    def try_to_add_location(self, geolocation: dict, first_key: str) -> str:
        """Try to get the name of country, subdivision or city.

        Args:
            geolocation (dict): Geolocation info.
            first_key (str): Country, subdivision or city.

        Returns:
            str: The name of country, subdivision or city.
        """
        try:
            geolocation = geolocation[first_key]
        except KeyError:
            return "::None"
        try:
            return f"::{geolocation['names']['en']}"
        except TypeError:
            return f"::{geolocation[0]['names']['en']}"

    def get_geolocation(self, ip: str) -> str:
        """Get proxy's geolocation.

        Args:
            ip (str): Proxy's ip.

        Returns:
            str: Proxy's geolocation.
        """
        geolocation = self.READER.get(ip)
        return (
            self.try_to_add_location(geolocation, "country")
            + self.try_to_add_location(geolocation, "subdivisions")
            + self.try_to_add_location(geolocation, "city")
        )

    def check(self, proxy: str, protocol: str) -> None:
        """Check proxy validity and append it to working_proxies.

        Args:
            proxy (str): ip:port.
            protocol (str): http/socks4/socks5.
        """
        try:
            ip = get(
                self.IP_SERVICE,
                proxies={
                    "http": f"{protocol}://{proxy}",
                    "https": f"{protocol}://{proxy}",
                },
                timeout=self.TIMEOUT,
            ).text.strip()
        except Exception:
            pass
        else:
            if (
                (self.MY_IP != ip)
                and (
                    not self.IPV4_ONLY or (self.IPV4_ONLY and self.is_ipv4(ip))
                )
                and (
                    not self.ANONYMOUS_ONLY
                    or (self.ANONYMOUS_ONLY and ip != proxy.split(":")[0])
                )
            ):
                if self.GEOLOCATION_MMDB:
                    proxy += self.get_geolocation(ip)
                self.working_proxies[protocol].append(proxy)

    def scrape(self, source: str, protocol: str) -> None:
        """Get proxies from source and append them to all_proxies.

        Args:
            source (str): Where to get the proxy list from.
            protocol (str): http/socks4/socks5.
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
                        self.all_proxies[protocol].append(proxy)
            else:
                print(f"ERROR {source} status code: {status_code}")

    def get_proxies(self, sources: tuple, protocol: str) -> None:
        """Run scraping and check certain protocol proxies.

        Args:
            sources (tuple): Where to get the proxy lists from.
            protocol (str): http/socks4/socks5.
        """
        print(f"Getting {protocol} proxy lists")
        self.all_proxies[protocol] = []
        self.start_threads(
            [
                Thread(target=self.scrape, args=(source.strip(), protocol))
                for source in sources
            ]
        )
        print(f"Checking {len(self.all_proxies[protocol])} {protocol} proxies")
        self.working_proxies[protocol] = []
        self.start_threads(
            [
                Thread(
                    target=self.check,
                    args=(
                        proxy.replace(f"{protocol}://", "").replace(
                            "https://", ""
                        ),
                        protocol,
                    ),
                )
                for proxy in tuple(set(self.all_proxies[protocol]))
            ]
        )
        with open(f"{protocol}_proxies.txt", "w", encoding="utf-8") as f:
            for proxy in sorted(self.working_proxies[protocol]):
                f.write(f"{proxy}\n")

    def main(self) -> None:
        """Start getting proxies."""
        self.all_proxies = {}
        self.working_proxies = {}
        if self.HTTP_SOURCES:
            self.get_proxies(self.HTTP_SOURCES, "http")
        if self.SOCKS4_SOURCES:
            self.get_proxies(self.SOCKS4_SOURCES, "socks4")
        if self.SOCKS5_SOURCES:
            self.get_proxies(self.SOCKS5_SOURCES, "socks5")
