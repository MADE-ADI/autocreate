#!/usr/bin/env python3
import argparse
import base64
import concurrent.futures
import json
import socket
import ssl
import time
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_HOST = "httpbin.org"
DEFAULT_PORT = 443
DEFAULT_PATH = "/ip"


def parse_proxy_line(line: str) -> Tuple[str, int, str, str]:
    raw = line.strip()
    if not raw:
        raise ValueError("baris kosong")

    parts = raw.split(":", 3)
    if len(parts) != 4:
        raise ValueError(
            "format proxy harus host:port:username:password"
        )

    host, port_text, username, password = parts
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError(f"port tidak valid: {port_text}") from exc

    return host, port, username, password


def recv_until_headers(sock: socket.socket) -> bytes:
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def test_proxy(proxy_line: str, timeout: float, target_host: str, target_port: int, target_path: str) -> Dict[str, object]:
    started_at = time.perf_counter()

    try:
        host, port, username, password = parse_proxy_line(proxy_line)
    except ValueError as exc:
        return {
            "proxy": proxy_line,
            "ok": False,
            "error": str(exc),
            "latency_ms": 0,
        }

    auth_token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    connect_request = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        f"Proxy-Authorization: Basic {auth_token}\r\n"
        "Proxy-Connection: Keep-Alive\r\n"
        "Connection: Keep-Alive\r\n\r\n"
    ).encode("utf-8")

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(connect_request)
            connect_response = recv_until_headers(sock).decode("iso-8859-1", errors="replace")

            status_line = connect_response.splitlines()[0] if connect_response else ""
            if " 200 " not in status_line:
                return {
                    "proxy": proxy_line,
                    "ok": False,
                    "error": f"CONNECT gagal: {status_line or 'tanpa respons'}",
                    "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
                }

            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=target_host) as tls_sock:
                tls_sock.settimeout(timeout)
                request = (
                    f"GET {target_path} HTTP/1.1\r\n"
                    f"Host: {target_host}\r\n"
                    "User-Agent: proxy-tester/1.0\r\n"
                    "Accept: application/json\r\n"
                    "Connection: close\r\n\r\n"
                ).encode("utf-8")
                tls_sock.sendall(request)

                response = b""
                while True:
                    chunk = tls_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk

        header_blob, _, body = response.partition(b"\r\n\r\n")
        status_line = header_blob.decode("iso-8859-1", errors="replace").splitlines()[0]
        if " 200 " not in status_line:
            return {
                "proxy": proxy_line,
                "ok": False,
                "error": f"request gagal: {status_line}",
                "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
            }

        body_text = body.decode("utf-8", errors="replace").strip()
        exit_ip = ""
        try:
            parsed = json.loads(body_text)
            if isinstance(parsed, dict):
                exit_ip = str(parsed.get("origin") or parsed.get("ip") or "")
        except json.JSONDecodeError:
            exit_ip = ""

        return {
            "proxy": proxy_line,
            "ok": True,
            "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
            "exit_ip": exit_ip,
            "response": body_text,
        }
    except Exception as exc:
        return {
            "proxy": proxy_line,
            "ok": False,
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
        }


def load_proxies(file_path: Path) -> List[str]:
    proxies: List[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            proxies.append(stripped)
    return proxies


def main() -> int:
    parser = argparse.ArgumentParser(description="Test daftar proxy dengan format host:port:user:pass")
    parser.add_argument("-f", "--file", default="proxy.txt", help="file daftar proxy")
    parser.add_argument("-t", "--timeout", type=float, default=8.0, help="timeout per proxy dalam detik")
    parser.add_argument("-w", "--workers", type=int, default=20, help="jumlah worker paralel")
    parser.add_argument("--host", default=DEFAULT_HOST, help="host tujuan untuk dites")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port tujuan untuk dites")
    parser.add_argument("--path", default=DEFAULT_PATH, help="path HTTP tujuan untuk dites")
    args = parser.parse_args()

    proxy_file = Path(args.file)
    if not proxy_file.exists():
        print(f"File tidak ditemukan: {proxy_file}")
        return 1

    proxies = load_proxies(proxy_file)
    if not proxies:
        print(f"Tidak ada proxy di file: {proxy_file}")
        return 1

    print(f"Memulai test {len(proxies)} proxy dari {proxy_file} ...")
    print(f"Target: https://{args.host}:{args.port}{args.path}\n")

    results: List[Dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(test_proxy, proxy, args.timeout, args.host, args.port, args.path): proxy
            for proxy in proxies
        }
        for index, future in enumerate(concurrent.futures.as_completed(future_map), start=1):
            result = future.result()
            results.append(result)
            status = "OK" if result["ok"] else "FAIL"
            latency = result.get("latency_ms", 0)
            message = result.get("exit_ip") or result.get("error") or ""
            print(f"[{index}/{len(proxies)}] {status:<4} {latency:>8} ms | {result['proxy']} | {message}")

    success = [item for item in results if item["ok"]]
    failed = [item for item in results if not item["ok"]]

    print("\nRingkasan")
    print(f"- Total   : {len(results)}")
    print(f"- Berhasil: {len(success)}")
    print(f"- Gagal   : {len(failed)}")

    if success:
        print("\nProxy yang berhasil:")
        for item in success:
            exit_ip = item.get("exit_ip") or "tidak terdeteksi"
            print(f"- {item['proxy']} -> {exit_ip} ({item['latency_ms']} ms)")

    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
