from odoo import models, fields, api
from uuid import uuid4


class PrintJob(models.Model):
    _name = 'print.job'
    _description = 'Print Job'
    _order = 'create_date desc'

    uuid = fields.Char(required=True, index=True, default=lambda self: str(uuid4()))
    printer_code = fields.Char(required=True, index=True)
    payload = fields.Binary(required=True)
    payload_type = fields.Selection([('pdf', 'PDF'), ('escpos', 'ESC/POS')], required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('printing', 'Printing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='pending', index=True)
    attempts = fields.Integer(default=0)
    error_message = fields.Text()
    create_date = fields.Datetime(readonly=True)
    write_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        ('uuid_unique', 'unique(uuid)', 'Print job UUID must be unique.')
    ]

    def mark_printing(self):
        for rec in self:
            rec.write({'state': 'printing', 'attempts': rec.attempts + 1})

    def mark_done(self):
        for rec in self:
            rec.write({'state': 'done', 'error_message': False})

    def mark_error(self, message):
        for rec in self:
            rec.write({'state': 'error', 'error_message': message or ''})

    def can_retry(self, max_attempts=5):
        self.ensure_one()
        return self.attempts < max_attempts
