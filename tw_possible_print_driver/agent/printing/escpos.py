import socket


def print_escpos(payload: bytes, printer_cfg: dict):
    ip = printer_cfg.get("ip")
    port = int(printer_cfg.get("port", 9100))
    timeout = float(printer_cfg.get("timeout", 5))
    if not ip:
        raise ValueError("printer_cfg.ip is required for escpos")
    with socket.create_connection((ip, port), timeout=timeout) as sock:
        sock.sendall(payload)
