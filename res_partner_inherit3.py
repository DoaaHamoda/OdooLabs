from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string="Related Patient")

    @api.constrains('related_patient_id')
    def _check_unique_patient_email(self):
        for record in self:
            patient = record.related_patient_id
            if patient and patient.email:
                conflicting_customers = self.search([
                    ('id', '!=', record.id),
                    ('related_patient_id', '!=', False),
                ])
                for customer in conflicting_customers:
                    if customer.related_patient_id.email == patient.email:
                        raise ValidationError(
                            f"This patient email '{patient.email}' is already linked to another customer (ID: {customer.id})."
                        )

    def unlink(self):
        for record in self:
            if record.related_patient_id:
                raise ValidationError("You cannot delete a customer linked to a patient.")
        return super().unlink()