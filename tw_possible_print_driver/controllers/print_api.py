import base64
from odoo import http
from odoo.http import request


def _is_https(req):
    proto = req.httprequest.headers.get('X-Forwarded-Proto') or req.httprequest.scheme
    return (proto or '').lower() == 'https'


def _check_bearer(req):
    auth = req.httprequest.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    token = auth.split(' ', 1)[1].strip()
    cfg = request.env['ir.config_parameter'].sudo()
    expected = cfg.get_param('tw.print.token')
    return token and expected and token == expected


class TwPrintAPI(http.Controller):
    @http.route('/tw/print/jobs', type='json', auth='none', methods=['GET'], csrf=False)
    def get_jobs(self, printer_code=None):
        if not _is_https(request):
            return {'error': 'https_required'}
        if not _check_bearer(request):
            return {'error': 'unauthorized'}

        domain = [('state', '=', 'pending')]
        if printer_code:
            domain.append(('printer_code', '=', printer_code))
        jobs = request.env['print.job'].sudo().search(domain, limit=20)
        # mark printing + attempts++ for idempotent delivery
        jobs.mark_printing()
        res = []
        for j in jobs:
            res.append({
                'uuid': j.uuid,
                'printer_code': j.printer_code,
                'payload_type': j.payload_type,
                'payload_base64': j.payload.decode() if isinstance(j.payload, bytes) else j.payload,
            })
        return {'jobs': res}

    @http.route('/tw/print/jobs/<string:uuid>/ack', type='json', auth='none', methods=['POST'], csrf=False)
    def ack_job(self, uuid, status=None, message=None):
        if not _is_https(request):
            return {'error': 'https_required'}
        if not _check_bearer(request):
            return {'error': 'unauthorized'}

        job = request.env['print.job'].sudo().search([('uuid', '=', uuid)], limit=1)
        if not job:
            return {'error': 'not_found'}
        if status == 'success':
            job.mark_done()
            return {'ok': True}
        else:
            job.mark_error(message or '')
            return {'ok': True}
