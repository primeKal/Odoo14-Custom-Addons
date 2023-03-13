from datetime import datetime
from datetime import timedelta
from pytz import timezone, UTC
from odoo.tools.misc import groupby
from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    appointment_group_id = fields.Many2one(string='Appointment Group', comodel_name='res.groups',
                                           config_parameter='s2u_online_appointment.appointment_group_id')

class ExtendSale(models.Model):
    _inherit = 'calendar.event'
    meetingLink = fields.Char(string='Meeting Link', default=False)

    eventLink = fields.Char(string='Event Link', default=False)

    def get_valid_appointment(self, **kwargs):
        valid_appointee = self.user_id
        appointment_date = kwargs.get('appointment_date', False) and datetime.strptime(kwargs.get('appointment_date'),
                                                                                       '%d/%m/%Y').date() or datetime.today().date()
        appointment_group_id = int(kwargs.get('calendar_group', self.env['ir.config_parameter'].sudo().get_param(
            's2u_online_appointment.appointment_group_id', 0)) or 0)
        appointment_group_id = self.env['res.groups'].browse(appointment_group_id)
        user_appointment_time = kwargs.get('appointment_time')
        if appointment_group_id.exists():
            stop_date = str(datetime.strptime(str(appointment_date),'%Y-%m-%d') + timedelta(hours=23,minutes=59))
            existing_calendar_events = self.search(
                [('start', '>=', appointment_date.strftime('%Y-%m-%d %T')), ('stop', '<=', stop_date),
                 ('partner_ids', 'child_of', appointment_group_id.users.mapped('partner_id.id'))])

            blocked_calendar_events = existing_calendar_events.filtered(
                lambda x: (UTC.localize(x.start) <= UTC.localize(user_appointment_time) <= UTC.localize(
                    x.stop)) or x.allday)
            existing_calendar_events = dict(groupby(existing_calendar_events, lambda x: x.user_id.id))
            filtered_user = appointment_group_id.users.filtered(
                lambda x: x.partner_id.id not in blocked_calendar_events.mapped('partner_ids').ids)
            if len(filtered_user):
                valid_appointee = filtered_user[0].id
        return valid_appointee