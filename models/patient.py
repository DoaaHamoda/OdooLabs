from odoo import models, fields, api, exceptions
import re
from datetime import date
from odoo.exceptions import ValidationError

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'
    _rec_name = 'first_name'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(compute='_compute_age', store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    email = fields.Char(string="Email")
    history = fields.Html()
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection([
        ('A', 'A'),('-A', '-A'),
        ('B', 'B'),('-B', '-B'),
        ('AB', 'AB'),('-AB', '-AB'),
        ('O', 'O'),('-O', '-O'),
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
    related_customer_id = fields.One2many('res.partner', 'related_patient_id', string="Related Customers")

    # doctors_id = fields.Many2many('hms.doctor')
    log_history_ids = fields.One2many('hms.patient.log', 'patient_id', string="Log History")
    res_partner_id = fields.Many2one('res.partner', string="Linked Partner")

    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Email must be unique.')
    ]

    def create_stat_log(self):
        vals = {
            'description': f"Changed stat to {self.status}",
            'patient': self.id
        }
        self.env['hms.patient.log'].create(vals)

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

    # @api.depends('age')
    # def _compute_show_history(self):
    #     for rec in self:
    #         rec.show_history = rec.age < 50

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

    @api.constrains('email')
    def _check_valid_email(self):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise exceptions.ValidationError("Email format is invalid.")

    @api.onchange('age')
    def _onchange_age_auto_check_pcr(self):
        if self.age and self.age < 30 and not self.pcr:
            self.pcr = True
        return {
                'warning': {
                    'title': 'PCR Automatically Checked',
                    'message': 'PCR was automatically checked because age is less than 30.'
                           }
            }

    @api.model
    def create(self, vals):
        patient = super(HmsPatient, self).create(vals)
        self.env['hms.patient.log'].create({
            'description': f'State changed to {patient.state}',
            'patient_id': patient.id,
            'created_by': self.env.user.id
        })
        return patient

    # def approve_action(self):
    #     for rec in self:
    #         if rec.state == 'undetermined':
    #             rec.state = 'good'
    #             self.env['hms.patient.log'].create({
    #                 'description': f'Patient {rec.display_name} approved',
    #                 'patient_id': rec.id,
    #                 'created_by': self.env.user.id
    #             })
    #         else:
    #             raise ValidationError("Patient is not in undetermined state.")

    def write(self, vals):
        for rec in self:
            old_state = rec.state
            res = super(HmsPatient, rec).write(vals)
            if 'state' in vals and vals['state'] != old_state:
                self.env['hms.patient.log'].create({
                    'patient_id': rec.id,
                    'description': f"State changed to {vals['state']}",
                    'created_by': self.env.uid
                })
        return res

    # @api.constrains('email')
    # def _check_valid_email(self):
    #     email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    #     for record in self:
    #         if record.email and not re.match(email_regex, record.email):
    #             raise exceptions.ValidationError("Email format is invalid.")

