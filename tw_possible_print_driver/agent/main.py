import base64
import json
import logging
import logging.handlers
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from printing.escpos import print_escpos
from printing.pdf import print_pdf

CONFIG_PATH = Path(__file__).with_name("config.json")
STATE_PATH = Path(__file__).with_name("state.json")
LOG_PATH = Path(__file__).with_name("agent.log")


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open('r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return default


def save_json(path: Path, data):
    try:
        with path.open('w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2)
    except Exception:
        pass


def setup_logging(log_path: Path):
    logger = logging.getLogger('agent')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logger.addHandler(stream)
    return logger


def build_opener(verify_ssl: bool):
    if verify_ssl:
        return urllib.request.build_opener()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    return urllib.request.build_opener(https_handler)


def get_jobs(cfg, opener, logger):
    base_url = cfg['odoo_url'].rstrip('/')
    printer_code = cfg.get('printer_code')
    query = ''
    if printer_code:
        query = '?printer_code=' + urllib.parse.quote(printer_code)
    url = f"{base_url}/tw/print/jobs{query}"
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f"Bearer {cfg['bearer_token']}")
    req.add_header('Accept', 'application/json')
    try:
        with opener.open(req, timeout=10) as resp:
            payload = resp.read()
            data = json.loads(payload.decode())
            return data.get('jobs', [])
    except urllib.error.HTTPError as e:
        logger.error("GET jobs failed: %s", e)
    except Exception as e:
        logger.error("GET jobs error: %s", e)
    return []


def post_ack(cfg, opener, uuid, status, message, logger):
    base_url = cfg['odoo_url'].rstrip('/')
    url = f"{base_url}/tw/print/jobs/{uuid}/ack"
    body = json.dumps({'status': status, 'message': message or ''}).encode()
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Authorization', f"Bearer {cfg['bearer_token']}")
    req.add_header('Content-Type', 'application/json')
    try:
        with opener.open(req, timeout=10) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        logger.error("ACK failed for %s: %s", uuid, e)
    except Exception as e:
        logger.error("ACK error for %s: %s", uuid, e)


def process_job(job, cfg, opener, logger, processed):
    uuid = job['uuid']
    if uuid in processed:
        logger.info("Skip already processed job %s", uuid)
        return
    try:
        payload_b64 = job['payload_base64']
        payload = base64.b64decode(payload_b64)
        printer_code = job['printer_code']
        printer_map = cfg.get('printer_map', {})
        printer_cfg = printer_map.get(printer_code)
        if not printer_cfg:
            raise ValueError(f"Unknown printer_code: {printer_code}")
        if job['payload_type'] == 'escpos':
            print_escpos(payload, printer_cfg)
        elif job['payload_type'] == 'pdf':
            print_pdf(payload, printer_cfg)
        else:
            raise ValueError(f"Unsupported payload_type: {job['payload_type']}")
        post_ack(cfg, opener, uuid, 'success', '', logger)
        processed.add(uuid)
        logger.info("Printed job %s", uuid)
    except Exception as e:
        logger.error("Job %s failed: %s", uuid, e)
        post_ack(cfg, opener, uuid, 'error', str(e), logger)


def main():
    cfg = load_json(CONFIG_PATH, {})
    if not cfg:
        raise SystemExit("Missing config.json; copy config.sample.json and adjust settings")
    opener = build_opener(cfg.get('verify_ssl', True))
    logger = setup_logging(LOG_PATH)
    processed = set(load_json(STATE_PATH, []))
    polling = cfg.get('polling_interval', 3)

    logger.info("Agent started; polling every %s seconds", polling)
    while True:
        jobs = get_jobs(cfg, opener, logger)
        for job in jobs:
            process_job(job, cfg, opener, logger, processed)
        if len(processed) > 1000:
            # keep state small
            processed = set(list(processed)[-500:])
        save_json(STATE_PATH, list(processed))
        time.sleep(polling)

if __name__ == '__main__':
    main()