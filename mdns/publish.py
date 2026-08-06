#!/usr/bin/env python3
import os
import socket
import sys
import time

from zeroconf import ServiceInfo, Zeroconf


def detect_ip() -> str:
    host_ip = os.environ.get("HOST_IP", "").strip()
    if host_ip:
        return host_ip

    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    finally:
        probe.close()


def is_likely_docker_internal(ip: str) -> bool:
    return ip.startswith("172.") or ip == "127.0.0.1"


def main() -> None:
    hostname = os.environ.get("MDNS_HOSTNAME", "carbonatix").strip().lower()
    port = int(os.environ.get("MDNS_PORT", "80"))
    ip = detect_ip()

    if is_likely_docker_internal(ip) and not os.environ.get("HOST_IP"):
        print(
            f"Detected Docker-internal IP ({ip}). "
            "Set HOST_IP in compose/.env to your WiFi LAN address.",
            file=sys.stderr,
        )

    fqdn = f"{hostname}.local."
    info = ServiceInfo(
        "_http._tcp.local.",
        f"{hostname}._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={"path": "/"},
        server=fqdn,
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print(f"Advertising http://{hostname}.local -> {ip}:{port}", flush=True)

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()


if __name__ == "__main__":
    main()
