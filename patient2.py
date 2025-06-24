from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'
    _rec_name = 'display_name'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(compute='_compute_age', store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
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
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], default='undetermined', string='State')
    department_id = fields.Many2one('hms.department', string='Department')
    doctor_ids = fields.Many2many('hms.doctor', string="Doctors")
    department_capacity = fields.Integer(
        related='department_id.capacity', readonly=True, store=True)
    show_history = fields.Boolean(compute="_compute_show_history", store=True)

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                rec.age = today.year - rec.birth_date.year - (
                    (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day)
                )
            else :
                rec.age = 0

    @api.depends('age')
    def _compute_show_history(self):
        for rec in self:
            rec.show_history = rec.age < 50

    @api.constrains('department_id')
    def _check_department_open(self):
        for rec in self:
            if rec.department_id and not rec.department_id.is_opened:
                raise ValidationError("Cannot assign a patient to a closed department.")

    @api.constrains('pcr', 'cr_ratio')
    def _check_cr_ratio_if_pcr(self):
        for rec in self:
            if rec.pcr and not rec.cr_ratio:
                raise ValidationError("CR Ratio is required if PCR is checked!")
