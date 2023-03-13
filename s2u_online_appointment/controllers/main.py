# -*- coding: utf-8 -*-
import json
import sys
import traceback

import pytz
import datetime

import werkzeug.utils
from pytz import utc, timezone
from odoo.exceptions import UserError
from odoo.addons.s2u_online_appointment.helpers import functions
from odoo.addons.s2u_online_appointment.controllers import test_calander_api

from odoo import http, modules, tools
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.http import request
import logging

from odoo.modules.module import get_module_resource,get_resource_path

import google_auth_oauthlib.flow
SCOPES = ['https://www.googleapis.com/auth/calendar']
_logger = logging.getLogger(__name__)


class OnlineAppointment(http.Controller):

    def _create_lead_from_appointment(self, data):
        opportunity = request.env['crm.lead'].sudo().create(data)
        return opportunity

    def ld_to_utc(self, ld, appointee_id, duration=False):

        date_parsed = datetime.datetime.strptime(ld, "%Y-%m-%d  %H:%M")
        if duration:
            date_parsed += datetime.timedelta(hours=duration)

        user = request.env['res.users'].sudo().search([('id', '=', appointee_id)])
        if user:
            if user.tz:
                tz = user.tz
            else:
                tz = 'Europe/Amsterdam'
            local = pytz.timezone(tz)
            local_dt = local.localize(date_parsed, is_dst=None)
            return local_dt.astimezone(pytz.utc)
        else:
            return ld

    def appointee_id_to_partner_id(self, appointee_id):

        appointee = request.env['res.users'].sudo().search([('id', '=', appointee_id)])
        if appointee:
            return appointee.partner_id.id
        else:
            return False

    def select_appointees(self, criteria='default', appointment_option=False):

        if not appointment_option:
            return []

        if appointment_option.user_specific:
            user_allowed_ids = appointment_option.users_allowed.ids
            slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', 'in', user_allowed_ids)])
            appointee_ids = [s.user_id.id for s in slots]
        else:
            slots = request.env['s2u.appointment.slot'].sudo().search([])
            appointee_ids = [s.user_id.id for s in slots]
        appointee_ids = list(set(appointee_ids))
        return appointee_ids

    def select_options(self, criteria='default'):

        return request.env['s2u.appointment.option'].sudo().search([])

    def prepare_values(self, form_data={}, default_appointee_id=False, criteria='default'):

        appointee_ids = self.select_appointees(criteria=criteria)
        options = self.select_options(criteria=criteria)

        values = {
            'appointees': request.env['res.users'].sudo().search([('id', 'in', appointee_ids)]),
            'appointment_options': options,
            'timeslots': [],
            'appointee_id': 0,
            'appointment_option_id': 0,
            'appointment_date': '',
            'timeslot_id': 0,
            'mode': 'public' if request.env.user._is_public() else 'registered',
            'name': request.env.user.partner_id.name if not request.env.user._is_public() else '',
            'email': request.env.user.partner_id.email if not request.env.user._is_public() else '',
            'phone': request.env.user.partner_id.phone if not request.env.user._is_public() else '',
            'remarks': '',
            'error': {},
            'group_id':form_data.get('calendar_group',''),
            'subject':form_data.get('subject',''),
            'error_message': [],
            'form_action': '/online-appointment/appointment-confirm',
            'form_criteria': criteria
        }

        if form_data:
            try:
                appointee_id = int(form_data.get('appointee_id', 0))
            except:
                appointee_id = 0

            try:
                appointment_option_id = int(form_data.get('appointment_option_id', 0))
            except:
                appointment_option_id = 0

            try:
                timeslot_id = int(form_data.get('timeslot_id', 0))
            except:
                timeslot_id = 0

            try:
                appointment_date = datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').strftime('%d/%m/%Y')
            except:
                appointment_date = ''

            values.update({
                'name': form_data.get('name', ''),
                'email': form_data.get('email', ''),
                'phone': form_data.get('phone', ''),
                'appointee_id': appointee_id,
                'appointment_option_id': appointment_option_id,
                'appointment_date': appointment_date,
                'timeslot_id': timeslot_id,
                'subject':form_data.get('subject',''),
                'remarks': form_data.get('remarks', '')
            })

            if appointee_id and appointment_option_id and appointment_date:
                free_slots = self.get_free_appointment_slots_for_day(appointment_option_id, form_data['appointment_date'], appointee_id, criteria)
                days_with_free_slots = self.get_days_with_free_slots(appointment_option_id,
                                                                     appointee_id,
                                                                     datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').year,
                                                                     datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').month,
                                                                     criteria)
                values.update({
                    'timeslots': free_slots,
                    'days_with_free_slots': days_with_free_slots,
                    'focus_year': datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').year,
                    'focus_month': datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').month
                })
        else:
            if values['appointees']:
                try:
                    default_appointee_id = int(default_appointee_id)
                except:
                    default_appointee_id = False
                if default_appointee_id and default_appointee_id in values['appointees'].ids:
                    values['appointee_id'] = default_appointee_id
                else:
                    values['appointee_id'] = values['appointees'][0].id
            if options:
                values['appointment_option_id'] = options[0].id
        return values

    @http.route(['/online-appointment','/online-appointment/<int:group_id>'], auth='public', website=True, csrf=True)
    def online_appointment(self, group_id=False, **kw):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param:
                ir_config = request.env['ir.config_parameter'].sudo().create({
                    'key': 's2u_online_appointment',
                    'value': 'public'
                })
            if not param or param.value.lower() != 'public':
                return request.render('s2u_online_appointment.only_registered_users')
        values = self.prepare_values(default_appointee_id=kw.get('appointee', False))
        values.update(group_id=group_id)
        return request.render('s2u_online_appointment.make_appointment', values)

    @http.route(['/online-appointment/appointment-confirm'], auth="public", type='http', website=True)
    def online_appointment_confirm(self, **post):
        error = {}
        error_message = []

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('s2u_online_appointment.only_registered_users')

            if not post.get('name', False):
                error['name'] = True
                error_message.append(_('Please enter your name.'))
            if not post.get('email', False):
                error['email'] = True
                error_message.append(_('Please enter your email address.'))
            elif not functions.valid_email(post.get('email', '')):
                error['email'] = True
                error_message.append(_('Please enter a valid email address.'))
            if not post.get('phone', False):
                error['phone'] = True
                error_message.append(_('Please enter your phonenumber.'))
        appointee_id = False
        # try:
        #     appointee_id = int(post.get('appointee_id', 0))
        # except:
        #     appointee_id = 0
        # if not appointee_id:
        #     error['appointee_id'] = True
        #     error_message.append(_('Please select a valid appointee.'))

        # option = request.env['s2u.appointment.option'].sudo().search([('id', '=', int(post.get('appointment_option_id', 0)))])
        # if not option:
        #     error['appointment_option_id'] = True
        #     error_message.append(_('Please select a valid subject.'))

        # slot = request.env['s2u.appointment.slot'].sudo().search([('id', '=', int(post.get('timeslot_id', 0)))])
        # if not slot:
        #     error['timeslot_id'] = True
        #     error_message.append(_('Please select a valid timeslot.'))
        try:
            date_start = False
            date_start = datetime.datetime.strptime(post['appointment_date'], '%d/%m/%Y')
        except :
            error['appointment_date'] = True
            error_message.append(_('Please select a valid date.'))
        try:
            appointment_datetime = False
            appointment_datetime = datetime.datetime.strptime(post.get('appointment_time'), '%Y-%m-%d %H:%M:%S')
            tz = post.get('tz') or request.env.user.tz or request.httprequest.cookies.get('tz')
            appointment_datetime = timezone(tz).localize(appointment_datetime)
            appointment_datetime = appointment_datetime.astimezone(utc)
            appointment_datetime = appointment_datetime.replace(tzinfo=None)
        except Exception as e:
            error['timeslot'] = True
            error_message.append(_("Please select a valid timeslot"))

        if len(post.keys()):
            appointee_id = request.env['calendar.event'].sudo().get_valid_appointment(
                **{**post, **{'appointment_time': appointment_datetime}})

        if not appointee_id:
            error['appointee_id'] = True
            error_message.append(_('Unable to find a valid appointee'))

        values = self.prepare_values(form_data=post)


        if error_message:
            values['error'] = error
            values['error_message'] = error_message
            return request.render('s2u_online_appointment.make_appointment', values)


        # if not self.check_slot_is_possible(option.id, post['appointment_date'], appointee_id, slot.id):
        #     values['error'] = {'timeslot_id': True}
        #     values['error_message'] = [_('Slot is already occupied, please choose another slot.')]
        #     return request.render('s2u_online_appointment.make_appointment', values)

        if request.env.user._is_public():
            partner = request.env['res.partner'].sudo().search(['|', ('phone', 'ilike', values['phone']),
                                                                     ('email', 'ilike', values['email'])])
            if partner:
                partner_ids = [self.appointee_id_to_partner_id(appointee_id),
                               partner[0].id]
            else:
                partner = request.env['res.partner'].sudo().create({
                    'name': values['name'],
                    'phone': values['phone'],
                    'email': values['email'],
                    'company_id': request.website.company_id.id
                })
                partner_ids = [self.appointee_id_to_partner_id(appointee_id),
                               partner[0].id]
        else:
            partner = request.env.user.partner_id
            partner_ids = [self.appointee_id_to_partner_id(appointee_id),
                           partner.id]

        # set detaching = True, we do not want to send a mail to the attendees
        duration = int(post.get('appointment_slot'))
        appointment = request.env['calendar.event'].sudo().with_context(detaching=True).create({
            'name': post.get('subject',''),
            'description': post.get('remarks', ''),
            'start': appointment_datetime,
            'stop': (appointment_datetime + datetime.timedelta(minutes=duration)).strftime(
                "%Y-%m-%d %H:%M:%S"),
            'duration': duration,
            'user_id':appointee_id,
            'partner_ids': [(6, 0, partner_ids)]
        })
        # set all attendees on 'accepted'
        appointment.attendee_ids.write({
            'state': 'accepted'
        })


        # registered user, we want something to show in his portal
        if not request.env.user._is_public():
            vals = {
                'partner_id': request.env.user.partner_id.id,
                'appointee_id': self.appointee_id_to_partner_id(appointee_id),
                'event_id': appointment.id
            }
            registration = request.env['s2u.appointment.registration'].create(vals)
        emails = [post['email']]
        start_time = post.get('appointment_time')
        startdto = appointment_datetime
        enddto = (startdto + datetime.timedelta(minutes=duration))
        sub = post.get('subject', '')
        remarks = post['remarks']
        # user = slot.user_id.email
        # if user:
        #     emails.append(user)
        try :
            demo = test_calander_api.create_meeting(start_time=startdto, emails=emails, end_time=enddto, subject=sub,
                                                    descri=remarks)
        except Exception as e:
            # _logger.info(e.with_traceback())
            traceback.print_exception(*sys.exc_info())
            raise UserError('error occured,please connect admin')
        appointment.write({
            'meetingLink': demo['meetLink'],
            'eventLink': demo['htmllink']
        })
        opportunity_id = self._create_lead_from_appointment({
            'partner_id': partner.id,
            'email_from': post['email'],
            'phone': post['phone'],
            'name': appointment.name,
            'description': remarks,
            'company_id': request.website.company_id.id,
            'user_id': False,
        })
        appointment.opportunity_id = opportunity_id
        return request.redirect('/online-appointment/appointment-scheduled?appointment=%d' % appointment.id)

    @http.route(['/online-appointment/appointment-scheduled'], auth="public", type='http', website=True)
    def confirmed(self, **post):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('s2u_online_appointment.only_registered_users')

        appointment = request.env['calendar.event'].sudo().search([('id', '=', int(post.get('appointment', 0)))])
        if not appointment:
            values = {
                'appointment': False,
                'error_message': [_('Appointment not found.')]
            }
            return request.render('s2u_online_appointment.thanks', values)

        if request.env.user._is_public():
            tz = request.httprequest.cookies['tz']
            start_time = utc.localize(appointment.start)
            start_time = start_time.astimezone(timezone(tz))
            start_time = start_time.replace(tzinfo=None)
            values = {
                'appointment': appointment,
                'start': start_time,
                'error_message': []
            }
            return request.render('s2u_online_appointment.thanks', values)
        else:
            if request.env.user.partner_id.id not in appointment.partner_ids.ids:
                values = {
                    'appointment': False,
                    'error_message': [_('Appointment not found.')]
                }
                return request.render('s2u_online_appointment.thanks', values)

            values = {
                'appointment': appointment,
                'error_message': []
            }
            return request.render('s2u_online_appointment.thanks', values)

    def check_slot_is_possible(self, option_id, appointment_date, appointee_id, slot_id):

        if not appointment_date:
            return False

        if not appointee_id:
            return False

        if not option_id:
            return False

        if not slot_id:
            return False

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return False
        slot = request.env['s2u.appointment.slot'].sudo().search([('id', '=', slot_id)])
        if not slot:
            return False

        date_start = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').strftime('%Y-%m-%d')

        # if today, then skip slots in te past (< current time)
        if date_start == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id) < datetime.datetime.now(pytz.utc):
            return False

        event_start = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id).strftime("%Y-%m-%d %H:%M:%S")
        event_stop = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id,
                                    duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")

        query = """
                SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                    WHERE ep.res_partner_id = %s AND
                          e.active = true AND                          
                          e.id = ep.calendar_event_id AND 
                        ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop >= %s) AND e.stop <= %s)                                       
        """
        request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                       event_start, event_stop,
                                       event_start, event_stop,
                                       event_start, event_stop))
        res = request.env.cr.fetchall()
        if not res:
            return True

        return False

    def filter_slots(self, slots, criteria):
        # override this method when slots needs to be filtered
        return slots

    def generate_free_time_slots(self, appointment_date, appointment_slot, appointment_group_id, tz=None):
        free_slots = {}
        user_timezone = tz or request.env.user.tz or request.httprequest.cookies.get('tz')
        calendar_obj = request.env['calendar.event'].sudo()
        start_date, stop_date = appointment_date, appointment_date + datetime.timedelta(hours=23, minutes=59)
        current_time = fields.Datetime.now()
        start_date = start_date.replace(hour=current_time.hour)
        if appointment_slot == 60:
            start_date = start_date + datetime.timedelta(hours=1)
        elif appointment_slot == 30:
            if current_time.minute < 30:
                start_date = start_date + datetime.timedelta(minutes=30)
            else:
                start_date = start_date + datetime.timedelta(hours=1)
        # utc_start_date = timezone(user_timezone).localize(start_date)
        utc_start_date = utc.localize(start_date)
        utc_stop_date = timezone(user_timezone).localize(stop_date)
        utc_stop_date = utc_stop_date.astimezone(utc)
        appointment_group = request.env['res.groups'].sudo().browse(int(appointment_group_id))
        existing_events = calendar_obj.search([('start', '>=', utc_start_date), ('stop', '<=', utc_stop_date), (
        'partner_ids', 'child_of', appointment_group.users.partner_id.ids)])
        is_not_last_slot_done = True
        # slot_start_date = timezone(user_timezone).localize(appointment_date + datetime.timedelta(hours=0))

        slot_start_date = utc_start_date.astimezone(timezone(user_timezone))
        slot_start_date = slot_start_date.replace(tzinfo=None)
        end_slot_time = slot_start_date + datetime.timedelta(hours=23, minutes=appointment_slot)
        all_day_events = list(set(appointment_group.mapped('users.partner_id.id')) - set(existing_events.filtered(lambda x: x.allday).partner_ids.ids))
        if not len(all_day_events):
            return free_slots
        while(is_not_last_slot_done):
            filtered_matched_event = list(filter(
                lambda x: fields.Datetime.context_timestamp(x.with_context(tz=user_timezone),
                                                            x.start) <= slot_start_date <= fields.Datetime.context_timestamp(
                    x.with_context(tz=user_timezone), x.stop), existing_events))
            filter_mutual_events = list(
                filter(lambda x: not len(set(appointment_group.mapped('users.partner_id.id')) - set(x.partner_ids.ids)),
                       filtered_matched_event))
            if len(filtered_matched_event) == len(appointment_group.users.ids) or len(filter_mutual_events):
                slot_start_date += datetime.timedelta(minutes=appointment_slot)
                _logger.info("I AM HERE {}".format(slot_start_date))
                continue
            free_slots.update({'{}'.format(slot_start_date.strftime('%H:%M %p')):slot_start_date})
            slot_start_date += datetime.timedelta(minutes=appointment_slot)
            is_not_last_slot_done = slot_start_date != end_slot_time
        return free_slots
    def get_free_appointment_slots_for_day(self, option_id, appointment_date, appointee_id, criteria):

        def slot_present(slots, slot):

            for s in slots:
                if s['timeslot'] == functions.float_to_time(slot):
                    return True
            return False

        if not appointment_date:
            return []

        if not appointee_id:
            return []

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return []

        week_day = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').weekday()
        slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', '=', appointee_id),
                                                                   ('day', '=', str(week_day))])
        slots = self.filter_slots(slots, criteria)

        date_start = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        free_slots = []
        for slot in slots:
            # skip double slots
            if slot_present(free_slots, slot.slot):
                continue

            # if today, then skip slots in te past (< current time)
            if date_start == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id) < datetime.datetime.now(pytz.utc):
                continue

            event_start = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id).strftime("%Y-%m-%d %H:%M:%S")
            event_stop = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot), appointee_id,
                                        duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")

            # check normal calendar events
            query = """
                    SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                        WHERE ep.res_partner_id = %s AND
                              e.active = true AND                               
                              e.id = ep.calendar_event_id AND 
                            ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop >= %s) AND e.stop <= %s)                                         
            """
            request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                           event_start, event_stop,
                                           event_start, event_stop,
                                           event_start, event_stop))
            res = request.env.cr.fetchall()
            if not res:
                free_slots.append({
                    'id': slot.id,
                    'timeslot': functions.float_to_time(slot.slot)
                })

        return free_slots

    def get_days_with_free_slots(self, option_id, appointee_id, year, month, criteria):

        if not option_id:
            return {}

        if not appointee_id:
            return {}

        start_datetimes = {}
        start_date = datetime.date(year, month, 1)
        for i in range(31):
            if start_date < datetime.date.today():
                start_date += datetime.timedelta(days=1)
                continue
            if start_date.weekday() not in start_datetimes:
                start_datetimes[start_date.weekday()] = []
            start_datetimes[start_date.weekday()].append(start_date.strftime('%Y-%m-%d'))
            start_date += datetime.timedelta(days=1)
            if start_date.month != month:
                break

        day_slots = []

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return {}

        for weekday, dates in start_datetimes.items():
            slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', '=', appointee_id),
                                                                       ('day', '=', str(weekday))])
            slots = self.filter_slots(slots, criteria)

            for slot in slots:
                for d in dates:
                    # if d == today, then skip slots in te past (< current time)
                    if d == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot), appointee_id) < datetime.datetime.now(pytz.utc):
                        continue

                    day_slots.append({
                        'timeslot': functions.float_to_time(slot.slot),
                        'date': d,
                        'start': self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot), appointee_id).strftime("%Y-%m-%d %H:%M:%S"),
                        'stop': self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot), appointee_id, duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")
                    })
        days_with_free_slots = {}
        for d in day_slots:
            if d['date'] in days_with_free_slots:
                # this day is possible, there was a slot possible so skip other slot calculations for this day
                # We only need to inform the visitor he can click on this day (green), after that he needs to
                # select a valid slot.
                continue

            query = """
                    SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                        WHERE ep.res_partner_id = %s AND 
                              e.active = true AND                              
                              e.id = ep.calendar_event_id AND  
                            ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop >= %s) AND e.stop <= %s)                                         
            """
            request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                           d['start'], d['stop'],
                                           d['start'], d['stop'],
                                           d['start'], d['stop']))
            res = request.env.cr.fetchall()
            if not res:
                days_with_free_slots[d['date']] = True
        return days_with_free_slots

    @http.route('/online-appointment/timeslots', type='json', auth='public', website=True)
    def free_timeslots(self, appointment_date, appointment_slot, appointment_group_id, tz, **kwargs):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return {
                    'timeslots': [],
                    'appointees': [],
                    'appointment_with': 0,
                    'days_with_free_slots': {},
                    'focus_year': 0,
                    'focus_month': 0,
                }

        try:
            date_parsed = datetime.datetime.strptime(appointment_date, '%d/%m/%Y')
            time_slot = int(appointment_slot)
        except:
            date_parsed = datetime.date.today()
            time_slot = 30

        free_time_slots = self.generate_free_time_slots(date_parsed, time_slot, appointment_group_id, tz)
        return free_time_slots

    @http.route('/online-appointment/month-bookable', type='json', auth='public', website=True)
    def month_bookable(self, appointment_option, appointment_with, appointment_year, appointment_month, form_criteria, **kwargs):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return {
                    'days_with_free_slots': [],
                    'focus_year': 0,
                    'focus_month': 0,
                }

        try:
            option_id = int(appointment_option)
        except:
            option_id = 0
        try:
            appointee_id = int(appointment_with)
        except:
            appointee_id = 0
        try:
            appointment_year = int(appointment_year)
            appointment_month = int(appointment_month)
        except:
            appointment_year = 0
            appointment_month = 0

        if not appointment_year or not appointment_month:
            appointment_year = datetime.date.today().year
            appointment_month = datetime.date.today().month

        days_with_free_slots = self.get_days_with_free_slots(option_id,
                                                             appointee_id,
                                                             appointment_year,
                                                             appointment_month,
                                                             form_criteria)

        return {
            'days_with_free_slots': days_with_free_slots,
            'focus_year': appointment_year,
            'focus_month': appointment_month,
        }

    def online_appointment_state_change(self, appointment, previous_state):
        # method to override when  you want something to happen on state change, for example send mail
        return True

    @http.route(['/online-appointment/portal/cancel'], auth="public", type='http', website=True)
    def online_appointment_portal_cancel(self, **post):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('s2u_online_appointment.only_registered_users')

        try:
            id = int(post.get('appointment_to_cancel', 0))
        except:
            id = 0

        if id:
            appointment = request.env['s2u.appointment.registration'].search([('id', '=', id)])
            if appointment and (
                    appointment.partner_id == request.env.user.partner_id or appointment.appointee_id == request.env.user.partner_id):
                previous_state = appointment.state
                appointment.cancel_appointment()
                self.online_appointment_state_change(appointment, previous_state)

        return request.redirect('/my/online-appointments')

    @http.route(['/online-appointment/portal/confirm'], auth="public", type='http', website=True)
    def online_appointment_portal_confirm(self, **post):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('s2u_online_appointment.only_registered_users')

        try:
            id = int(post.get('appointment_to_confirm', 0))
        except:
            id = 0

        if id:
            appointment = request.env['s2u.appointment.registration'].search([('id', '=', id)])
            if appointment and (
                    appointment.partner_id == request.env.user.partner_id or appointment.appointee_id == request.env.user.partner_id):
                previous_state = appointment.state
                appointment.confirm_appointment()
                self.online_appointment_state_change(appointment, previous_state)

        return request.redirect('/my/online-appointments')
    @http.route('/returned',
                type='http', auth='public', csrf=False, methods=['GET', 'POST'], save_session=False)
    def authReturn(self, **post):

        _logger.info('S2U------retrieved callback from google saving to token file')
        req = request.httprequest
        cc = req.url
        # return request.redirect('/payment/process')
        json_token_file = get_module_resource('s2u_online_appointment', 'static/', 'credentials.json')
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            json_token_file, scopes=SCOPES,)

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        flow.redirect_uri = base_url +'/returned'

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = cc
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        _logger.info('S2U-----here will through error for localhost')

        _logger.info('S2U-----we have recieved the response so we can save to file')
        json_token_file = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
        with open(json_token_file, 'w+', encoding="utf-8") as token:
            # token.write('fdhfdjdfhjdf')
            token.write(json.loads(credentials))
        _logger.info('success in savinggggg')
        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        return werkzeug.utils.redirect(base_url)

