# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ctypes import sizeof
from http import client
import base64
import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import pprint
import operator
import os
import re
import sys
import tempfile
# from numpy import True_
import json

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata
from datetime import timedelta,datetime

from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.event.controllers.main import EventController
from odoo.http import request
from odoo.osv import expression
from odoo.tools.misc import get_lang, format_date


import werkzeug
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.exceptions import NotFound

from ast import literal_eval
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo
from odoo.addons.base.models.res_partner import Partner
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.osv.expression import OR



_logger = logging.getLogger(__name__)
import string
# import africastalking



_logger = logging.getLogger(__name__)



class WebRegisteration(AuthSignupHome):
    
    
    @http.route('/success', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.redirect('/shop')
    
    @http.route('/joinus', type='http',  auth='public', website=True)
    def membershipsignup(self,  **kw):
        _logger.info("_________________________")
        projects = request.env['project.project'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        country_state = request.env['res.country.state'].sudo().search([])

        mentees = request.env['res.partner'].sudo().search([('member_type','=','mentee')])
        _logger.info(mentees) 
        partner = request.env.user.partner_id
        return http.request.render('member_dashboard.membership_register', {
            "mentees": mentees,
            "projects": projects,
            "partner": partner,
            "country": country,
            "country_state": country_state
            
            })



    @http.route('/get_states', type='http',  auth='public', website=True)
    def getstates(self,  **kw):
        _logger.info("_________________________")
        country = kw.get('country')
        _logger.info(country)
        count = request.env['res.country'].search([('id','=', int(country))])
        _logger.info(count)
        states = request.env['res.country.state'].search([('country_id','=',count.id)])
        _logger.info('this is the states we found')
        _logger.info(states)
        dd = []
        for state in states:
            dd.append({'id': state.id,'name':state.name})
        _logger.info(dd)
        res = {'states': dd}
        return werkzeug.wrappers.Response(json.dumps(res))
        # return { 'states': states}



    @http.route('/mentee/select', type='http',  auth='public', website=True)
    def menteeSelect(self,  **kw):
        _logger.info("###############")
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        project = request.env['project.project'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        country_state = request.env['res.country.state'].sudo().search([])
        mentees = request.env['res.partner'].sudo().search([('member_type','=','mentee'),('mentee_state','in',['waiting','free'])])

        return http.request.render('member_dashboard.mentee_select',{"users":users,"search_from_res_partner":search_from_res_partner, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,"project":project,"mentees":mentees})

    



    @http.route('/mentor/info', type='http',  auth='public', website=True)
    def mentorinfo(self,  **kw):
        _logger.info("###############")
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        project = request.env['project.project'].sudo().search([])
        return http.request.render('member_dashboard.mentor_info',{"users":users,"search_from_res_partner":search_from_res_partner, "search_from_res_users":search_from_res_users, "users_mentor":users_mentor,"project":project})

    
    
    @http.route('/my/dashboard', type='http',  auth='public', website=True)
    def mydashboard(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None,   **kw):
        project = request.env['project.project'].sudo().search([])
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        if not partner_id.approved_acc:
            return http.request.render('member_dashboard.not_approved')
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        total_sales = request.env['sale.order'].sudo().search_count([])
        order = request.env['sale.order'].sudo().search([])
        total = []
        for line in order:
            vals = {}
            vals = line.amount_total
            total.append(vals)
        _logger.info(total)
        value = 0
        total_price = sum(total)
        _logger.info(total_price)
       
        # _logger.info(total_ssearch_from_res_partnerales)
        total_vistor = request.env['res.partner'].sudo().search_count([])
        _logger.info(total_vistor)
        

        return http.request.render('member_dashboard.my_dashboard',{
            "projects":project,"total_sales":total_sales,"total_vistor":total_vistor,
            "users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,
            "search_from_res_partner":search_from_res_partner,
            "total_price":total_price})

    @http.route('/my/chart', type='http',  auth='public', website=True)
    def mychart(self,  **kw):
        return http.request.render('member_dashboard.my_chart')

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, page=1, date_begin=None, date_end=None, project=None,
             sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'),
                       'order': 'date_last_stage_update desc'},
        }
        project_val = ''
        if request.params and request.params.get('project', False):
            project_val = '?project=' + str(request.params.get('project'))
        projects = request.env['project.project'].search(
            [('privacy_visibility', '=', 'portal')])
        cookie_value = request.httprequest.cookies.get('project_id_cookie')
        project_filters = {
            'all': {'label': '', 'domain': []},
        }
        for proj in projects:
            project_filters.update({
                str(proj.id): {'label': proj.name,
                               'domain': [('project_id', '=', proj.id)]}
            })
        domain = [('project_id.privacy_visibility', '=', 'portal')]
        domain += project_filters.get(project, project_filters['all'])[
            'domain']
        order = sortings.get(sortby, sortings['date'])['order']
        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project.task', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]
        # pager
        pager = request.website.pager(
            url="/my/home",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'project': project},
            total=request.env['project.task'].search_count([]),
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        tasks = request.env['project.task'].search(domain, order=order,
                                                   limit=self._items_per_page,
                                                   offset=pager['offset'])
        default_sprints = False
        sprints = request.env['project.scrum.sprint'].sudo().search(
            [('project_id.id', '=', request.params.get('project'))])
        for spr in sprints:
            if spr.state == 'open':
                default_sprints = \
                    request.env['project.scrum.sprint'].sudo().search(
                        [('state', '=', 'open'),
                         ('project_id.id', '=', request.params.get('project'))])[
                        0].id
            else:
                default_sprints = \
                    request.env['project.scrum.sprint'].sudo().search(
                        [('project_id.id', '=', request.params.get('project'))])[
                        0].id
        project_dashbord = request.env['project.project'].sudo().search(
            [('id', '=', request.params.get('project'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'project_filters': OrderedDict(sorted(project_filters.items())),
            'projects': projects,
            'project': project,
            'sortings': sortings,
            'sortby': sortby,
            'tasks': tasks,
            'sprints': sprints,
            'project_dashbord': project_dashbord,
            'page_name': 'task',
            'archive_groups': archive_groups,
            'default_url': '/my/home',
            'pager': pager,
            'cookie_value': cookie_value,
            'project_val': project_val,
            'default_sprints': default_sprints
        })
        return request.render("portal.portal_my_home", values,{"users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,"search_from_res_partner":search_from_res_partner,})

    @http.route('/my/complian', type='http',  auth='public', website=True)
    def mycomplian(self,  **kw):
        mentee_id =  request.session.uid
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        complaints = request.env['complaint.category'].sudo().search([])

       
        project = request.env['project.project'].sudo().search([])
        return http.request.render('member_dashboard.my_complian',{
            "users":users,
            "search_from_res_users":search_from_res_users,
            "users_mentor":users_mentor,
            "project":project,
            "search_from_res_partner":search_from_res_partner,
            "complaints":complaints,
            "users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,
            })


    @http.route('/report/feedback', type='http',  auth='public', website=True)
    def myreports(self,  **kw):
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        partner_id = request.env.user.partner_id
       
            
        return http.request.render('member_dashboard.my_report', {"partner_id":partner_id,"search_from_res_partner":search_from_res_partner,"users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,})

    
    
    

    
    
    @http.route(['/my/event', '/event/page/<int:page>', '/events', '/events/page/<int:page>'], type='http', auth="public", website=True)
    def events(self, page=1, **searches):
        Event = request.env['event.event']
        SudoEventType = request.env['event.type'].sudo()
        _logger.info(http.request.env.context.get('uid'))
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        searches.setdefault('search', '')
        searches.setdefault('date', 'all')
        searches.setdefault('tags', '')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        website = request.website
        today = fields.Datetime.today()

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)

        def _extract_searched_event_tags(self, searches):
            tags = request.env['event.tag']
            if searches.get('tags'):
                try:
                    tag_ids = literal_eval(searches['tags'])
                except:
                    pass
                else:
                    # perform a search to filter on existing / valid tags implicitely + apply rules on color
                    tags = request.env['event.tag'].search([('id', 'in', tag_ids)])
            return tags

        def get_month_filter_domain(filter_name, months_delta):
            first_day_of_the_month = today.replace(day=1)
            filter_string = _('This month') if months_delta == 0 \
                else format_date(request.env, value=today + relativedelta(months=months_delta),
                                 date_format='LLLL', lang_code=get_lang(request.env).code).capitalize()
            return [filter_name, filter_string, [
                ("date_end", ">=", sd(first_day_of_the_month + relativedelta(months=months_delta))),
                ("date_begin", "<", sd(first_day_of_the_month + relativedelta(months=months_delta+1)))],
                0]

        dates = [
            ['all', _('Upcoming Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            get_month_filter_domain('month', 0),
            ['old', _('Past Events'), [
                ("date_end", "<", sd(today))],
                0],
        ]

        # search domains
        domain_search = {'website_specific': website.website_domain()}

        if searches['search']:
            domain_search['search'] = [('name', 'ilike', searches['search'])]

        # search_tags = self._extract_searched_event_tags(searches)
        # if search_tags:
        #     # Example: You filter on age: 10-12 and activity: football.
        #     # Doing it this way allows to only get events who are tagged "age: 10-12" AND "activity: football".
        #     # Add another tag "age: 12-15" to the search and it would fetch the ones who are tagged:
        #     # ("age: 10-12" OR "age: 12-15") AND "activity: football
        #     grouped_tags = defaultdict(list)
        #     for tag in search_tags:
        #         grouped_tags[tag.category_id].append(tag)
        #     domain_search['tags'] = []
        #     for group in grouped_tags:
        #         domain_search['tags'] = expression.AND([domain_search['tags'], [('tag_ids', 'in', [tag.id for tag in grouped_tags[group]])]])

        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]

        if searches["type"] != 'all':
            current_type = SudoEventType.browse(int(searches['type']))
            domain_search["type"] = [("event_type_id", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = request.env['res.country'].browse(int(searches['country']))
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        def dom_without(without):
            domain = []
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = Event.search_count(dom_without('date') + date[2])

        domain = dom_without('type')

        domain = dom_without('country')
        countries = Event.read_group(domain, ["id", "country_id"], groupby="country_id", orderby="country_id")
        countries.insert(0, {
            'country_id_count': sum([int(country['country_id_count']) for country in countries]),
            'country_id': ("all", _("All Countries"))
        })

        step = 12  # Number of events per page
        event_count = Event.search_count(dom_without("none"))
        pager = website.pager(
            url="/event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'date_begin desc'
        order = 'is_published desc, ' + order
        events = Event.search(dom_without("none"), limit=step, offset=pager['offset'], order=order)

        keep = QueryURL('/event', **{key: value for key, value in searches.items() if (key == 'search' or value != 'all')})

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events,  # event_ids used in website_event_track so we keep name as it is
            'dates': dates,
            'categories': request.env['event.tag.category'].search([]),
            'countries': countries,
            'pager': pager,
            "search_from_res_partner":search_from_res_partner,
            'searches': searches,
            "users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,
            # 'search_tags': search_tags,
            'keep': keep,
        }

        if searches['date'] == 'old':
            # the only way to display this content is to set date=old so it must be canonical
            values['canonical_params'] = OrderedMultiDict([('date', 'old')])

        return request.render("member_dashboard.index", values)


    @http.route('/register/reset_password', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.render('custom_web.reset_password')
    
        
    @http.route('/my/profile', type='http',  auth='public', website=True)
    def my_profile(self,  **kw):
        profile = request.env['res.partner'].sudo().search([('id','=',1)])
        return http.request.render('member_dashboard.my_profile',{"profile":profile})
          
        
    @http.route('/api/fileupload', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def upload_image(self, **kw):
        _logger.info("##############IN UPLOAD ##############")
        _logger.info(request.httprequest.files.getlist('image'))
        _logger.info(request.httprequest.files.getlist('file'))
        _logger.info(kw)
        
        files = request.httprequest.files.getlist('file')
        _logger.log("########### files:%s",files)

    @http.route('/share-your-idea', type='http',  auth='public', website=True)
    def ideas(self,  **kw):
        country = request.env['res.country'].sudo().search([])

        return http.request.render('member_dashboard.shear_ideas',{"country":country})

    @http.route('/contact-us', type='http',  auth='public', website=True)
    def contactus(self,  **kw):
        company = request.env['res.company'].sudo().search([])

        
        return http.request.render('member_dashboard.contact_us',{"company":company})

   
    #membership feedback 
    @http.route('/feedback_submit',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_feedback(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            feedback = request.env['report.report'].sudo().create({
                "user_id": kw.get('user_id'),
                # "date": today,
                "how_did_you_find": kw.get('how_did_you_find'),
                "how_often_do_you": kw.get('how_often_do_you'),
                "your_participation": kw.get('your_participation'),
                "rate_your_level": kw.get('rate_your_level'),
                "how_do_you_evaluate": kw.get('how_often_do_you'),
                "suggestions": kw.get('suggestions') 
                })

            _logger.info(feedback)
            # return werkzeug.utils.redirect('/my/dashboard')
            return request.render('member_dashboard.feedback_submitted')


    @http.route('/register/mentor', type='http',  auth='public', website=True)
    def mentorregister(self,  **kw):
        _logger.info("Excuting here ##########################")
        projects = request.env['project.project'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        country_state = request.env['res.country.state'].sudo().search([])
        mentees = request.env['res.partner'].sudo().search([('member_type','=','mentee')])

        return http.request.render('custom_web.mentor',{
            "mentees": mentees,
            "country": country,
            "country_state": country_state
        })

  
    @http.route('/register/mentor', type='http',  auth='public', website=True)
    def mentorregister(self,  **kw):
        _logger.info("Excuting here ##########################")
        projects = request.env['project.project'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        country_state = request.env['res.country.state'].sudo().search([])
        mentees = request.env['res.partner'].sudo().search([('member_type','=','mentee')])

        return http.request.render('custom_web.mentor',{
            "mentees": mentees,
            "country": country,
            "country_state": country_state
        })

    @http.route('/register/mentee', type='http',  auth='public', website=True)
    def menteeregister(self,  **kw):
        _logger.info("Excuting here ##########################")
        projects = request.env['project.project'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        country_state = request.env['res.country.state'].sudo().search([])
        mentees = request.env['res.partner'].sudo().search([('member_type','=','mentee')])
        return http.request.render('custom_web.mentee',{
            "country": country,
            "country_state": country_state
        })


    #Shear Ideas 
    @http.route('/api/shear/ideas',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def shearIdeas(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])

            shearIdea = request.env['crm.lead'].sudo().create({
                "comment_type": "Ideas Sheared",
                "name": "Ideas Sheared by  " + kw.get('name'),
                "volunteer_name": kw.get('your_participation'),
                "volunteer_email": kw.get('email'),
                "email_from": kw.get('email'),
                "volunteer_address": kw.get('address'),
                "volunteer_country": country.id,
                "what_do_you_want": kw.get('what_do_you_want') ,
                "never_again": kw.get('never_again') 

                })

           
            return werkzeug.utils.redirect('/contactus-thank-you')
            # return request.render('member_dashboard.feedback_submitted')


    #COntact Us
    @http.route('/api/contact_us',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def contact_Us(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])

            shearIdea = request.env['crm.lead'].sudo().create({
                "comment_type": "Comment",
                "name": "Commented by  " + kw.get('name'),
                "email_from": kw.get('email'),
                "phone": kw.get('phone'),
                "description":  kw.get('subject')+"\n\n"+ kw.get('message'),
               

                })

           
            return werkzeug.utils.redirect('/contactus-thank-you')
            # return request.render('member_dashboard.feedback_submitted')

   
    #membership compliant 
    @http.route('/complian_submit',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_complaint(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            complaint = request.env['member.complaint'].sudo().create({
                "user_id": kw.get('user_id'),
                "victim_id": kw.get('victim_id'),
                "subject": kw.get('subject'),
                "complaint_category": kw.get('complaint_id'),
                "circumstances": kw.get('message') 
                })

            _logger.info(complaint) 
            return request.render('member_dashboard.complaint_submitted')

            # return request.render('member_dashboard.my_dashboard')

    
    #Thanks popup
    @http.route('/complian/submit', type='http', auth='public', website=True, sitemap=False)
    def complian(self, *args, **kw):
        _logger.info(kw)

        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        partner_id = request.env.user.partner_id
       
        return request.render('member_dashboard.complaint_submitted',{"partner_id":partner_id,"users":users, "search_from_res_users":search_from_res_users,"users_mentor":users_mentor,})
                
    #Mentee Selction
    #Mentor signup
    @http.route('/api/mentee/select',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def menteeselectSave(self, *args, **kw):
        _logger.info("############# create mentor selection ###############")
        _logger.info(kw)
        today = datetime.today()
        _logger.info(today)
        mentee_id = request.env['res.partner'].sudo().search([('id','=', kw.get('mentee_id'))], limit=1)
        mentor_id = request.env['res.partner'].sudo().search([('id','=', kw.get('mentor_id'))], limit=1)
            
        mapping = request.env['mentor.mapping'].create({
                "mentor_id": kw.get('mentor_id'),
                "mentee_id": kw.get('mentee_id'),
                "date_from": today,  
        }) 
        mentor_id.update({
            "mentee_state": "waiting"
                })
        mentee_id.update({
            "mentee_state": "waiting"
        })

        _logger.info(mapping)
        return werkzeug.utils.redirect('/my/dashboard')
    
    
    #Mentor signup
    @http.route('/api/mentor/register',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def mentroregisterUpload(self, *args, **kw):
        _logger.info("############# create mentor  ###############")
        _logger.info(kw)
        qcontext = self.get_auth_signup_qcontext()
        # print(kw)
        _logger.info("qcontext: %s",qcontext)
        

        _logger.info("qcontext: %s",qcontext)
        data = kw
        email = kw.get("login")

        try:
            _logger.info("oooooooooooooooooooooooooo")
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            self.send(qcontext.get('login'))
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            mentee_id = request.env['res.partner'].sudo().search([('id','=', kw.get('mentees'))], limit=1)
            mentor_id = request.env['res.partner'].sudo().search([('name','=', kw.get('name')),('email','=',kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])
            country_state = request.env['res.country.state'].sudo().search([('id','=',kw.get("state_id"))])
            if partner_id:
                partner_id.write({
                "member_type": kw.get('type'),
                "phone": kw.get('phone'),
                "select_mentee": mentee_id.id,
                "country_id": country,
                "state_id": country_state,
                "city": kw.get('city'),
                "zip": kw.get('zip'),
                "gender": kw.get('gender'),
                "years_of_profession": kw.get('years_of_profession'),
                "business_areas": kw.get('business_areas'),
                "description": kw.get('description'),
                "Have_been_mentor": kw.get('Have_been_mentor'),
                "experience": kw.get('experience'),
                "Why_are_you_interested": kw.get('Why_are_you_interested'),
                "free_member": "1",   
                "social_media": kw.get('social'),
                "instagram": kw.get('instagram'),
                "twitter": kw.get('twitter'),
                "linkedin": kw.get('linkedin') 
                })


            if kw and request.httprequest.method == 'POST':
                _logger.info("pppppppppppppppicture %s",kw.get('image_1920'))
                partner_id = request.env.user.partner_id
                _logger.info(partner_id)
               
                image_1920 = kw.get('image_1920')
                if image_1920:
                    FileStorage = kw.get('image_1920')
                    FileData = FileStorage.read()
                    file_base64 = base64.encodestring(FileData)


                    name = kw.get('image_1920').filename
                    file = kw.get('image_1920')
                    image_1920 = image_1920.read()
                    image_1920 = base64.b64encode(image_1920)
                    _logger.info(image_1920)
                    res = request.env.user.partner_id.sudo().write({
                        'image_1920': file_base64
                    })
                # Update mentor and mentee Mapping
                _logger.info("________________________ Updateing Mapping table_____________________________")
            
                _logger.info(mentor_id)
                _logger.info(mentee_id)
                today = datetime.today()
                _logger.info(today)

                mentor_id.update({
                    "mentee_state": "waiting"
                })
                mentee_id.update({
                    "mentee_state": "waiting"
                })
                mapping = request.env['mentor.mapping'].create({
                        "mentor_id": mentor_id.id,
                        "mentee_id": mentee_id.id,
                        "date_from": today,  
                }) 

                _logger.info(mapping)
                # return werkzeug.utils.redirect('/home-1')
                return werkzeug.utils.redirect('/web/session/logout')
            # if data:
            #     search_crm = request.env['crm.lead'].sudo().search([(
            #         'email_from','=',email
            #     )], limit=1)
            #     if len(search_crm) > 0:
            #         pass
            #     else:
            #         create = request.env['crm.lead'].sudo().create({
            #             'name': 'Mentors',
            #             'partner_id':partner_id.id,
            #             'email_from': data['login']
            #         })
                    
                    # if create:
                    #     return werkzeug.utils.redirect('/forum/helpcenter-1')
                    #     return {
                    #             "success": True,
                    #             "message": 'Successfull created'
                    #         }
                    # else:
                    #     return {
                    #             "success": False,
                    #             "message": "Something went wrong"
                    #         }
                    
                    # return werkzeug.utils.redirect('/home-1')
               
            else:
                return {
                        "success": False,
                        "message": "Something went wrong"
                    }
 
        except Exception as e:
            # qcontext['error'] = e.args[0]
            _logger.info('----------------------------------------------error---------------------------------')
            _logger.info(e.args[0])
            qcontext['error'] = 'Failed, Email already registered'
       
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


     # # Mentee register
    @http.route('/api/mentee/register',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def menteedataupload(self, *args, **kw):
        _logger.info("############# create mentee  ###############")
        _logger.info(kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("qcontext: %s",qcontext)
        

        _logger.info("qcontext: %s",qcontext)
        data = kw
        email = kw.get("login")

        try:
            _logger.info("oooooooooooooooooooooooooo")
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            self.send(qcontext.get('login'))
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            mentee_id = request.env['res.partner'].sudo().search([('id','=', kw.get('mentees'))], limit=1)
            mentor_id = request.env['res.partner'].sudo().search([('name','=', kw.get('name')),('email','=',kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])
            country_state = request.env['res.country.state'].sudo().search([('id','=',kw.get("state_id"))])
           
            if partner_id:
                partner_id.write({
                    "member_type": kw.get('type'),
                    "phone": kw.get('phone'),
                    "country_id": country,
                    "state_id": country_state,
                    "city": kw.get('city'),
                    "zip": kw.get('zip'),
                    "gender": kw.get('gender'),
                    "whoyouare": kw.get('whoyouare'),
                    "hobby": kw.get('hobby'),
                    "education_background": kw.get('education_background'),
                    "school_performace": kw.get('school_performace'),
                    "Have_been_mentee": kw.get('Have_been_mentee'),
                    "experience": kw.get('experience'),
                    "free_member": "1",
                    "social_media": kw.get('social'),
                    "instagram": kw.get('instagram'),
                    "twitter": kw.get('twitter'),
                    "linkedin": kw.get('linkedin')   
                    })   
                
            if kw and request.httprequest.method == 'POST':
                _logger.info("pppppppppppppppicture %s",kw.get('image_1920'))
                partner_id = request.env.user.partner_id
                _logger.info(partner_id)
               
                image_1920 = kw.get('image_1920')
                if image_1920:
                    FileStorage = kw.get('image_1920')
                    FileData = FileStorage.read()
                    file_base64 = base64.encodestring(FileData)


                    name = kw.get('image_1920').filename
                    file = kw.get('image_1920')
                    image_1920 = image_1920.read()
                    image_1920 = base64.b64encode(image_1920)
                    _logger.info(image_1920)
                    res = request.env.user.partner_id.sudo().write({
                        'image_1920': file_base64
                    })
                # return werkzeug.utils.redirect('/home-1')
                return werkzeug.utils.redirect('/web/session/logout')
            # if data:
            #     # attachment = files[0].read()
            #     search_crm = request.env['crm.lead'].sudo().search([(
            #         'email_from','=',email
            #     )], limit=1)
            #     if len(search_crm) > 0:
            #         pass
            #     else:
            #         create = request.env['crm.lead'].sudo().create({
            #             'name': 'Mentors',
            #             'partner_id':partner_id.id,
            #             'email_from': data['login'],
            #             # 'phone': data['phone'],
            #             # 'resume': base64.encodebytes(attachment),
            #         })
                    
                    # if create:
                    #     return werkzeug.utils.redirect('/forum/helpcenter-1')
                    #     # return {
                    #     #         "success": True,
                    #     #         "message": 'Successfull created'
                    #     #     }
                    # else:
                    #     return {
                    #             "success": False,
                    #             "message": "Something went wrong"
                    #         }
                    
                    # return werkzeug.utils.redirect('/home-1')
                    
               
            else:
                return {
                        "success": False,
                        "message": "Something went wrong"
                    }
 
        except Exception as e:
            # qcontext['error'] = e.args[0]
            _logger.info('cauth errrrrrrrrrrrrrrrrrrrprrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrorrrrrrrrrrrrrrrrrrrrrrr')
            _logger.info('----------------------------------------------error---------------------------------')
            _logger.info(e.args[0])
            qcontext['error'] = 'Failed, Email already registered'
       
       
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
      

    
      
    #Mentroship Registration api

    @http.route('/membership_signup',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_signup(self, *args, **kw):
        _logger.info(kw)
        qcontext = self.get_auth_signup_qcontext()
        print(kw)
        _logger.info("qcontext: %s",qcontext)
        
        # FileStorage = kw.get('image_1920')
        # FileData = FileStorage.read()
        # file_base64 = base64.encodestring(FileData)


        # name = kw.get('image_1920').filename
        # file = kw.get('image_1920')

        # profile = {
        #     'image_1920_1920':base64.b64encode(file.read()),

        # }

        # files = request.httprequest.files.getlist('image_1920')
        # attachment = files.read()
        # 'image_1920_1920': base64.encodestring(attachment)
        # post['image_1920'].read().encode('base64')}

        projects = request.httprequest.form.getlist('projects[]')
        mentees = request.httprequest.form.getlist('mentees[]')
        
        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            self.send(qcontext.get('login'))
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            mentee_id = request.env['res.partner'].sudo().search([('id','=', mentees)], limit=1)
            mentor_id = request.env['res.partner'].sudo().search([('name','=', kw.get('name')),('email','=',kw.get('login'))], limit=1)
            # request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1).write({"free_member": "1",   
            #         "image_1920":file_base64})
            # _logger.info(projects)
            vals = []
            pro = {}
            for project in projects:
                
                product_id = request.env['project.project'].sudo().search([('id','=', project)], limit=1)
                _logger.info(product_id)
                pro['project_contribute'] = product_id
                
                vals.append(pro)
            _logger.info(vals)
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])
            country_state = request.env['res.country.state'].sudo().search([('id','=',kw.get("state_id"))])
            _logger.info(country)
            _logger.info(country_state)
            partner_id.update({
                "project_contribute": projects,
                "free_member": "1",
                "select_mentee": mentee_id.id,
                "country_id": country,
                "state_id": country_state,
                "city": kw.get("city"),
                "phone": kw.get("phone"),
                "member_type": "freemember",
                #  'image_1920':base64.b64encode(file.read()
            })
           


            

            # return request.render('http://207.154.229.160:8069/shop')
            # return werkzeug.utils.redirect('/home-1')
            return werkzeug.utils.redirect('/web/session/logout')
        
        except Exception as e:
            # qcontext['error'] = e.args[0]
            _logger.info('----------------------------------------------error---------------------------------')
            _logger.info(e.args[0])
            qcontext['error'] = 'Failed, Email already registered'
            
        # response = request.render('auth_signup.signup', qcontext)
        response = request.render('auth_signup.signup', qcontext)

        response.headers['X-Frame-Options'] = 'DENY'
        return response
    def send(self,email):
        print('sending')
        _logger.info('hellooooooo')
        _logger.info(email)
        mail_pool = request.env['mail.mail'].sudo()
        values={}
        _logger.info('-------------------------hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii---------------------------')
        values.update({'subject': 'Haqi Membership Submitted'})
        values.update({'email_to': email})
        values.update({'body_html': 'Dear applicant, your request to join HAQI has been received. Our system will get back to you with a response over the next few days. Thank you for your interest!' })
        values.update({'body': 'Dear applicant, your request to join HAQI has been received. Our system will get back to you with a response over the next few days. Thank you for your interest!' })
        # values.update({'res_id': 'obj.id' }) #[optional] here is the record id, where you want to post that email after sending
        # values.update({'model': ''Object Name }) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending
        msg_id = mail_pool.create(values)
        _logger.info(msg_id) 
        if msg_id:
            msg_id.send()
            # mail_pool.send([msg_id])
      

    @http.route('/signupformset', type='http', auth='public', website=True, sitemap=False)
    def signupformset(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        try:
            _logger.info("oooooooooooooooooooooooooo")
            self.do_signup(qcontext)
            
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            if partner_id:
                partner_id.write({
                    "free_member": "1",  
                    })
               
            # if res_user_id:
            #     res_user_id.partner_id.write({
            #         "age": kw.get('age'),
            #         "phone": kw.get('phone')
            #     })
            #     res_user_id.write({
            #         "age": kw.get('age')
            #     })
                
            #     _logger.info("res_user: %s", pprint.pformat(res_user_id))
            #     _logger.info("res.partner: %s",  pprint.pformat(partner_id))
                        
            return request.render('register.sign_up_thanks')
            
        
        except UserError as e:
            qcontext['error'] = e.args[0]
       
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
      
      
    #Custome forget password form Website side 
    
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def custom_reset_password2(self, *args, **kw):
        _logger.info("############# custom reset password form website ##############")
        _logger.info("Data:%s",kw)
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    # assert phone, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(phone)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response  
    
    
        
        
        
    
    ###### This for Json [APP register Form]
    
    @http.route('/api/registerform', type='json', auth='public', website=False, sitemap=False)
    def registerForm(self, *args, **kw):
        _logger.info("############# Values form Json ###############")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("qcontext: %s",qcontext)

        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                    
            _logger.info("________________________ Write Custom fileds_____________________________")

            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            if res_user_id:
                res_user_id.partner_id.write({
                    "age": kw.get('age'),
                    "phone": kw.get('phone')
                })
                
                _logger.info("res_user: %s", res_user_id)
                _logger.info("res.partner: %s",  partner_id)
                    
                return {
                    "success": True,
                    "message": "Successfully registered"
                        
                        }

            
        except:
            return {
                "success": False,
                "message": "Something went wrong"
                     
            }
            
    
    

        
        
        

        
    
    
 
class CustomSignin(Home):
    
    
    @http.route('/web/signin', type='http',  auth='public', website=True)
    def signin_webform(self,  **kw):
        _logger.info("##########################")
        return http.request.render('register.sign_in_form')
        # return "Hello hkkkku" #request.render('register.sign_up_form',{})
    
    
    ### Website login
     
    @http.route('/membership_signin', type='http',website=True, auth='none')
    def membership_signin(self, redirect=None, **kw): 
        _logger.info("************** Membership  Sign in ****************")
        _logger.info("Data: %s",kw)
        _logger.info(request.params)
        email = kw.get("login")
        password = kw.get("password")
        
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('http://localhost:8069/shop')
        # response = request.render('web.login', values)

        response.headers['X-Frame-Options'] = 'DENY'
        return response

 
       
    
class AuthSignupHome(Home):
    
    # Website Reset Password 
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def member_web_auth_resetpassword(self, *args, **kw):
        _logger.info("**************** custom Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                _logger.info("*********** ***************")
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info("*********** Searching phone number user***************")
                    
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('phone','=',phone)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('phone','=',phone)], limit=1)
                    
                    _logger.info("Search_result:%s User Name: %s  phone: %s",search_user, search_user.name, search_user.phone)
                    # assert phone, _("No phone provided.")
                    _logger.info("search_user:%s",search_user)
                    response = request.render('register.confirm_reset_password',{"search_user":search_user})
                    phont_len = str(phone)
                    _logger.info(len(phont_len))
                    
                    
                    if  search_user.phone != phone:
                        qcontext['error'] = _("Invalid phone number")
                    elif  len(phont_len) == 10 and re.search("^[0-9]+$", phont_len) and search_user.phone == phone is not None:
                        _logger.info("************ 10 digit  right user*************") 
                        
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        ## here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            phone = str(phone)
                            partner_id.write({
                                'verification_code':verification
                            })
                            
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        
                        return response
                    elif  len(phont_len) == 13:
                        _logger.info("************ 13 digits  right user*************") 
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        partner_id.write({
                                'verification_code':verification
                            })
                        ### here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            
                           
                            
                            partner_id.write({
                                'verification_code':verification
                            })
                            _logger.info("verification_code writed on res partner: %s",partner_id.verification_code)
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        return response
                    else:
                        qcontext['error'] = _("Incorrect phone number")
                   
            except UserError as e:
                
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    #confirm password reset with verification
    
    @http.route('/register/web/confirm_reset_password', type='http', auth='public', website=True, sitemap=False)
    def member_web_auth_confirm_reset_password(self, *args, **kw):
        _logger.info("**************** Confirm Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
               
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('id','=',kw.get('user_id'))], limit=1)
                    _logger.info(search_user)
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    if kw.get('password') != kw.get("cpassword"):
                        qcontext['error'] = _("Password Not Match")

                    elif kw.get('password') == kw.get("cpassword"): # and search_user.phone == phone:
                        _logger.info("************ Correct password  match *************")
                        result = request.env['res.users'].sudo().confirm_reset_password(qcontext)
                        _logger.info("Finallly result: %s",result)
                        
                      
                        response = request.render('register.sign_in_form')
                        
                        return response
                    else:
                        qcontext['error'] = _("Invalid password  ")
                    
            except UserError as e:
                
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.confirm_reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    #App Side password reset
    
    @http.route('/register/api/reset_password', type='json', auth='public', website=False, sitemap=False)
    def member_web_auth_reset_passwordApp(self, *args, **kw):
        _logger.info("**************** App  Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                _logger.info("*********** ***************")
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info("*********** Searching phone number user***************")
                    
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('phone','=',phone)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('phone','=',phone)], limit=1)
                    
                    _logger.info("Search_result:%s User Name: %s  phone: %s",search_user, search_user.name, search_user.phone)
                    # assert phone, _("No phone provided.")
                    _logger.info("search_user:%s",search_user)
                    # response = request.render('register.confirm_reset_password',{"search_user":search_user})
                    phont_len = str(phone)
                    _logger.info(len(phont_len))
                    
                    
                    if  search_user.phone != phone:
                        qcontext['error'] = _("Invalid phone number")
                    elif  len(phont_len) == 10 and re.search("^[0-9]+$", phont_len) and search_user.phone == phone is not None:
                        _logger.info("************ 10 digit  right user*************") 
                        
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        ## here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            phone = str(phone)
                            partner_id.write({
                                'verification_code':verification
                            })
                            username = "ETTADEV"   # use 'sandbox' for development in the test environment
                            api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
                            africastalking.initialize(username, api_key)
                            sms = africastalking.SMS
                            sms_response = sms.send(f"{verification} is your verification code for ZODO", [f"+251{phone}"],"8707")
                            partner_id.write({
                                'verification_code':verification
                            })
                            return {
                                    "success": True,
                                    "result":{
                                        'verification_code':verification,
                                        'phone':search_user.phone,
                                        'userId':search_user.id
                                    },
                                    "message": "Verfication successfully Sent"
                                    }
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                             return {
                                    "success": False,
                                    "message": "Something went wrong"
                                    }
                            
                        
                       
                    elif  len(phont_len) == 13:
                        _logger.info("************ 13 digits  right user*************") 
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        partner_id.write({
                                'verification_code':verification
                            })
                        ### here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            
                            username = "ETTADEV"   # use 'sandbox' for development in the test environment
                            api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
                            africastalking.initialize(username, api_key)
                            sms = africastalking.SMS
                            sms_response = sms.send(f"{verification} is your verification code for ZODO", [phone],"8707")
                            
                            partner_id.write({
                                'verification_code':verification
                            })
                            _logger.info("verification_code writed on res partner: %s",partner_id.verification_code)
                            return {
                                    "success": True,
                                    "result":{
                                        'verification_code':verification,
                                        'phone':search_user.phone,
                                        'userId':search_user.id
                                    },
                                    "message": "Verfication successfully Sent"
                                    }
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                             return {
                                    "success": False,
                                    "message": "Something went wrong"
                                    }
                    else:
                        
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                   
            except UserError as e:
                
                return {
                            "success": False,
                            "message": "Something went wrong"
                        }



    #App Side confirm password reset with verification
    
    @http.route('/register/api/confirm_reset_password', type='json', auth='public', website=False, sitemap=False)
    def member3_web_auth_confirm_reset_password(self, *args, **kw):
        _logger.info("**************** Appside Confirm Reset password With Verfication Code ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
               
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('id','=',kw.get('user_id'))], limit=1)
                    _logger.info(search_user)
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    if kw.get('password') != kw.get("cpassword"):
                        qcontext['error'] = _("Password Not Match")

                    elif kw.get('password') == kw.get("cpassword"): # and search_user.phone == phone:
                        _logger.info("************ Correct password  match *************")
                        result = request.env['res.users'].sudo().confirm_reset_password(qcontext)
                        _logger.info("Finallly result: %s",result)
                        
                      
                        return {
                            "success": True,
                            "message": "Successfully Reset"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                    
            except:
                return {
                            "success": False,
                            "message": "Something went wrong"
                        }
           
    
    
    


        
    
    
   