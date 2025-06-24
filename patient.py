from odoo import models, fields, api
from datetime import date

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient Information'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date()
    history = fields.Html()
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ], string="Blood Type")
    pcr = fields.Boolean(string="PCR Test")
    image = fields.Binary(string="Patient Image")
    address = fields.Text()
    age = fields.Integer(compute='_compute_age', store=True)

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                record.age = today.year - record.birth_date.year - ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
            else:
                record.age = 0
