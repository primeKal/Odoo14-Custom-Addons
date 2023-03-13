import json
import random
import logging
import werkzeug.utils
import requests
from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND
from odoo.tools import convert
from odoo.exceptions import Warning, UserError, AccessDenied
import inspect
import hashlib
import os
import sys
import string
from datetime import datetime,timedelta
import base64
import traceback
import re

_logger = logging.getLogger(__name__)


CLEANR = re.compile(
    '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


class OrganizationController(http.Controller):

    def create_or_get(self, model, field, value, vals=None, create=False):
        fields = [(i, '=', j) for i, j in zip(field, value)]
        # fields.append(limit=1)
        _logger.info(fields)
        db_result = request.env[f"{model}"].sudo().search(fields, limit=1)
        if db_result:
            return db_result.id
        else:
            if create:
                created_result = request.env[f"{model}"].sudo().create(vals)
                return created_result.id
            else:
                return None



    def create_automated_matches_from_event(self,event,duration):
        _logger.info('Beginning creating')
        number_of_court = event.field_of_play.number_of_court
        expected_games_per_court = event.expected_game_per_court
        # researve one court for off set
        offset = (number_of_court-1) % expected_games_per_court
        games_per_court = int((number_of_court-1)/expected_games_per_court)
        for court in range(number_of_court):
            start_time = datetime.now()
            for x in range(games_per_court):
                _logger.info('creating match')
                # name = even at court(x-1) at time start_time
                team = self.create_or_get('team.team',('name','=','Demo Team'),{
                    'name': 'Demo Team',
                    'organization_id': event.organization_id
                });
                if team :
                    match = request.env["match.match"].sudo().create(
                        {
                            'team_1': team.id,
                            'team_2': team.id,
                            'name': f"Demo Match at Court {court+1},Match {x+1}",
                            'event_id' : event.id,
                            'start_date_time': start_time,
                            'end_date_time': (start_time + duration)
                        }
                    )
                start_time = start_time + timedelta(hours=duration.hour, minutes=duration.minute())


    @http.route('/api/organization/create_event', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_event(self, **kw):
        _logger.info("##############IN EVENT##############")
        _logger.info(kw)
        _logger.info("##############IN EVENT##############")
        event_data = kw.get("event")
        server_token = kw.get("server_token")
        sport_type = kw.get("sport_type")
        location = kw.get("location")
        field_of_play = kw.get("field_of_play")
        rules = kw.get("rules")
        try:
            organization = request.env["organization.organization"].sudo().search(
                [('id', '=', event_data['organization_id']), ('server_token', '=', server_token)], limit=1)

            if organization:

                added_field_of_play = []
                for fp in field_of_play:
                    fp_id = self.create_or_get('event.court.types', ['name'], [f"{fp['name']}"], vals={
                        "name": fp['name']
                    }, create=True)
                    field = request.env["event.court.numbers"].sudo().create({
                        "court_type": fp_id,
                        "number_of_court": fp['number_of_court']
                    })
                    added_field_of_play.append(field.id)
                event_data['field_of_play'] = added_field_of_play

                added_rule = []
                for rule in rules:
                    rule_id = self.create_or_get("event.rule.type", ['name'], [f"{rule['name']}"], vals={
                        "name": rule['name']
                    }, create=True)
                    added_rule.append(rule_id)
                event_data['rules'] = added_rule

                added_sport_type_list = []
                for sport_t in sport_type:
                    sport_type_id = self.create_or_get('sport.type', ['name'], [f"{sport_t['name']}"], vals={
                        "name": f"{sport_t['name']}"
                    }, create=True)
                    added_sport_type_list.append(sport_type_id)
                event_data['sport_type'] = added_sport_type_list

                # added_locations = []
                # for loc in locations:
                country = location['country']
                country_id = self.create_or_get("res.country", ['name'], [f"{country['name']}"],
                                                vals={"name": f"{country['name']}"}, create=True)
                state = location['state']
                vals = state
                vals['country_id'] = country_id
                state_id = self.create_or_get("res.country.state", ['name'], [f"{state['name']}"], vals=vals,
                                              create=True)
                created_location = request.env["location.location"].sudo().create({
                    "country": country_id,
                    "state": state_id,
                    "name": location['name']
                    # "long": loc['long'],
                    # "lat": loc['lat']
                })
                # added_locations.append(created_location.id)
                event_data['location'] = created_location.id
                _logger.info(event_data)
                request.env.cr.commit()
                event = request.env["event.event"].sudo().create(event_data)
                if event:
                    return {
                        "success": True,
                        "event": event.toJson()
                    }
                else:
                    return {
                        "success": False,
                        "message": "Something went wrong"
                    }
            else:
                return {
                    "success": False,
                    "message": "Invalid server token",
                    "error_code": 111
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/create_match', type='json', auth='public', csrf=False)
    def create_match(self, **kw):
        _logger.info("##############IN MATCH##############")
        _logger.info(kw)
        _logger.info("##############IN MATCH##############")
        match_data = kw.get("match")
        rules = kw.get("rules")
        team_1 = kw.get("team_1")
        team_2 = kw.get("team_2")
        sport_type = kw.get("sport_type")
        # location = kw.get("location")
        # country = location.get("country")
        # state = location.get("state")
        server_token = kw.get("server_token")
        organization_id = kw.get("organization_id")
        team_1_new = kw.get("team_1_new")
        team_2_new = kw.get("team_2_new")
        try:
            if team_1_new or team_2_new:
                if team_1_new and team_2_new:
                    if type(team_1) != dict and type(team_2) != dict:
                        return {
                            "success": False,
                            "message": "Invalid team data provided"
                        }
                else:
                    if team_1_new:
                        if type(team_1) != dict or type(team_2) != int:
                            return {
                                "success": False,
                                "message": "Invalid team data provided"
                            }
                    if team_2_new:
                        if type(team_2) != dict or type(team_1) != int:
                            return {
                                "success": False,
                                "message": "Invalid team data provided"
                            }
            else:
                if type(team_1) != int or type(team_2) != int:
                    return {
                        "success": False,
                        "message": "Invalid team ID"
                    }

            organization = request.env["organization.organization"].sudo().search(
                [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)

            if organization:
                event_organization = request.env["event.event"].sudo().search(
                    [('organization_id', '=', organization.id), ('id', '=', match_data['event_id'])], limit=1)
                if event_organization:

                    # country_id = self.create_or_get("res.country", ['name'], [f"{country['name']}"],
                    #                                 vals={"name": f"{country['name']}"}, create=True)
                    # vals = state
                    # vals['country_id'] = country_id
                    # state_id = self.create_or_get("res.country.state", ['name'], [f"{state['name']}"], vals=vals,
                    #                             create=True)
                    # created_location = request.env["location.location"].sudo().create({
                    #     "country": country_id,
                    #     "state": state_id,
                    #     "name": location['name'],
                    #     # "long": location['long'],
                    #     # "lat": location['lat']
                    # })
                    # match_data['location_id'] = created_location.id

                    sport_type_id = self.create_or_get('sport.type', ['name'], [f"{sport_type['name']}"], vals={
                        "name": f"{sport_type['name']}"
                    }, create=True)
                    match_data['sport_type'] = sport_type_id

                    if team_1_new or team_2_new:
                        if team_1_new:
                            team_1['organization_id'] = organization.id
                            team_1['sport_type'] = sport_type_id
                            if not team_2_new:
                                search_team_2 = request.env['team.team'].sudo().search(
                                    [('name', '=', f"{organization.id}-Away Team"), ('organization_id', '=', organization.id)], limit=1)
                                if team_2 != -99:
                                    search_team_2 = request.env['team.team'].sudo().search(
                                        [('id', '=', team_2), ('organization_id', '=', organization.id)], limit=1)
                                if search_team_2:
                                    match_data['team_2'] = search_team_2.id
                                    created_team_1 = request.env["team.team"].sudo().create(
                                        team_1)
                                    match_data['team_1'] = created_team_1.id
                                else:
                                    return {
                                        "success": False,
                                        "message": "Team data not found."
                                    }
                            else:
                                created_team_1 = request.env["team.team"].sudo().create(
                                    team_1)
                                match_data['team_1'] = created_team_1.id
                        if team_2_new:
                            team_2['sport_type'] = sport_type_id
                            team_2['organization_id'] = organization.id
                            if not team_1_new:
                                search_team_1 = request.env['team.team'].sudo().search(
                                    [('name', '=', f"{organization.id}-Home Team"), ('organization_id', '=', organization.id)], limit=1)
                                if team_1 != -99:
                                    search_team_1 = request.env['team.team'].sudo().search(
                                        [('id', '=', team_1), ('organization_id', '=', organization.id)], limit=1)
                                if search_team_1:
                                    match_data['team_1'] = search_team_1.id
                                    created_team_2 = request.env["team.team"].sudo().create(
                                        team_2)
                                    match_data['team_2'] = created_team_2.id
                                else:
                                    return {
                                        "success": False,
                                        "message": "Team data not found."
                                    }
                            else:
                                created_team_2 = request.env["team.team"].sudo().create(
                                    team_2)
                                match_data['team_2'] = created_team_2.id
                        # created_team_1 = request.env["team.team"].sudo().create(team_1)
                        # created_team_2 = request.env["team.team"].sudo().create(team_2)

                        # match_data['team_1'] = created_team_1.id
                        # match_data['team_2'] = created_team_2.id
                    else:
                        search_team_1 = request.env['team.team'].sudo().search(
                            [('name', '=', f"{organization.id}-Home Team"), ('organization_id', '=', organization.id)], limit=1)
                        if team_1 != -99:
                            search_team_1 = request.env['team.team'].sudo().search(
                                [('id', '=', team_1), ('organization_id', '=', organization.id)], limit=1)
                        search_team_2 = request.env['team.team'].sudo().search(
                            [('name', '=', f"{organization.id}-Away Team"), ('organization_id', '=', organization.id)], limit=1)
                        if team_2 != -99:
                            search_team_2 = request.env['team.team'].sudo().search(
                                [('id', '=', team_2), ('organization_id', '=', organization.id)], limit=1)
                        if search_team_1 and search_team_2:
                            match_data['team_1'] = search_team_1.id
                            match_data['team_2'] = search_team_2.id
                        else:
                            return {
                                "success": False,
                                "message": "Team data not found."
                            }

                    # added_rule_list = []
                    # for rule in rules:
                    #     rule_id = self.create_or_get('event.rule.type', ['name'], [f"{rule['name']}"], vals={
                    #         "name": f"{rule['name']}"
                    #     }, create=True)
                    #     added_rule_list.append(rule_id)
                    # match_data['rules'] = added_rule_list

                    match_data['date_of_event'] = datetime.strptime(f"{match_data['date_of_event']} 00:00:00",
                                                                    '%d/%m/%Y %H:%M:%S').date()
                    match_data['start_date_time'] = datetime.strptime(
                        match_data['start_date_time'], '%d/%m/%Y %H:%M:%S')
                    match_data['end_date_time'] = datetime.strptime(
                        match_data['end_date_time'], '%d/%m/%Y %H:%M:%S')

                    _logger.info(match_data)
                    match = request.env["match.match"].sudo().create(
                        match_data)
                    if match:
                        return {
                            "success": True,
                            "event": match.toJson()
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }

                else:
                    return {
                        "success": False,
                        "message": "This organization do not have access to this event."
                    }

            else:
                return {
                    "success": False,
                    "message": "Invalid server token",
                    "error_code": 111
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    # @http.route('/api/organization/create_coach', type='json', auth='public', website=False, csrf=False)

    @http.route('/api/organization/create_coach', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_coach(self, **kw):
        _logger.info("##############IN COACH##############")
        _logger.info(kw)
        _logger.info("##############IN COACH##############")
        coach_data = kw.get("coach")
        organization_id = kw.get("organization_id")
        user_data = kw.get("user")
        server_token = kw.get("server_token")
        try:
            if coach_data and organization_id and user_data and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    coach_data['organization'] = organization.id

                    search_user = request.env["res.users"].sudo().search(
                        [('login', '=', user_data['login'])], limit=1)
                    if not search_user:
                        user = request.env["res.users"].sudo().create(
                            user_data)
                        coach_data['user_id'] = user.id

                        created_coach = request.env["coach.coach"].sudo().create(
                            coach_data)
                        if coach_data:
                            return {
                                "success": True,
                                "coach": created_coach.toJson()
                            }
                        else:
                            return {
                                "success": False,
                                "message": "Something went wrong."
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Email already taken"
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }

            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/assign_coach', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def assign_coach(self, **kw):
        _logger.info("##############IN ASSIGN COACH##############")
        _logger.info(kw)
        _logger.info("##############IN ASSIGN COACH##############")
        organization_id = kw.get("organization_id")
        team_id = kw.get("team_id")
        coach_id = kw.get("coach_id")
        server_token = kw.get("server_token")
        try:
            if coach_id and team_id and organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    team = request.env["team.team"].sudo().search(
                        [('id', '=', team_id), ('organization_id', '=', organization.id)], limit=1)
                    if team:
                        coach = request.env["coach.coach"].sudo().search(
                            [('id', '=', coach_id), ('organization', '=', organization.id)], limit=1)
                        if coach:
                            team.coach_id = coach.id
                            return {
                                "success": True,
                                "team": team.toJson()
                            }
                        else:
                            return {
                                "success": False,
                                "message": "Coach data not found"
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Team data not found"
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
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

    @http.route('/api/organization/get_organization_events', type='json', auth='public', website=True, csrf=False,
                method=['POST'])
    def get_organization_events(self, **kw):
        try:
            organization_id = kw.get("organization_id")
            server_token = kw.get("server_token")
            organization = request.env["organization.organization"].sudo().search(
                [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
            if organization:
                events = request.env["event.event"].sudo().search([('organization_id', '=', organization_id)],
                                                                  order="id desc")
                return {
                    "success": True,
                    "events": [event.toJson() for event in events]
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid server token.",
                    "error_code": 111
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/get_event_match', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_event_match(self, **kw):
        _logger.info("##############IN GET EVENT MATCH##############")
        _logger.info(kw)
        _logger.info("##############IN GET EVENT MATCH##############")
        event_id = kw.get("event_id")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        try:
            if event_id and organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    event = request.env["event.event"].sudo().search(
                        [('id', '=', event_id), ('organization_id', '=', organization_id)])
                    if event:
                        matches = request.env["match.match"].sudo().search(
                            [('event_id', '=', event.id)])
                        if matches:
                            match_list = []
                            for match in matches:
                                match_list.append(match.toJson())
                            return {
                                "success": True,
                                "match_list": match_list
                            }
                        else:
                            return {
                                "success": True,
                                "match_list": []
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Event not found."
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token.",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "Please provide all fields."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

# Organization Creating Teams
    # http://127.0.0.1:8069/api/organization/create_team/

    # Json Body

    # {
    #     "params": {
    #         "team": {
    #             "name": "Team Four",
    #             "crew_size": 22,
    #             "team_type": "teamA"
    #         },
    #         "sport_type": {
    #             "name": "Volley Ball"
    #         },
    #         "organization_id": 1,
    #         "server_token": "HAPEYVHHUwsrGtDhvRtcaGJWbTGkSD"
    #     }
    # }

    @http.route('/api/organization/get_coaches', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_coaches(self, **kw):
        _logger.info("##############GET COACHES##############")
        _logger.info(kw)
        _logger.info("##############GET COACHES##############")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        try:
            if organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    coaches = request.env["coach.coach"].sudo().search(
                        [('organization', '=', organization_id)], order="id desc")
                    coaches_list = []
                    for coach in coaches:
                        coaches_list.append(coach.toJson())
                    return {
                        "success": True,
                        "coaches_list": coaches_list
                    }

                else:
                    return {
                        "success": False,
                        "message": "Invalid server token.",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "All fields are required."
            }

    @http.route('/api/organization/create_team', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_team(self, **kw):
        _logger.info("****************** Registering Team ****************")
        _logger.info(kw)
        team_data = kw.get("team")
        sport_type = kw.get("sport_type")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        _logger.info(team_data.get("name"))
        try:
            if team_data and organization_id and sport_type and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    search_team = request.env["team.team"].sudo().search(
                        [('name', '=', team_data.get("name")), ('organization_id', '=', organization_id)], limit=1)
                    if search_team:
                        return {
                            "success": False,
                            "message": "The Team  already Registered",
                            "teams": search_team.toJson()
                        }

                    else:

                        sport_type_id = self.create_or_get('sport.type', ['name'], [f"{sport_type['name']}"],
                                                           vals={
                            "name": f"{sport_type['name']}"
                        }, create=True)

                        team_data['sport_type'] = sport_type_id
                        team_data['organization_id'] = organization.id
                        created_team = request.env["team.team"].sudo().create(
                            team_data)
                        if team_data:
                            return {
                                "success": True,
                                "teams": created_team.toJson()

                            }
                        else:
                            return {
                                "success": False,
                                "message": "Something went wrong."
                            }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }

            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/get_referees', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_referees(self, **kw):
        _logger.info("###############IN GET REFEREES######################")
        _logger.info(kw)
        _logger.info("###############IN GET REFEREES######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        try:
            if organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    referees = request.env["referees.referees"].sudo().search([
                    ])
                    ref_list = []
                    for ref in referees:
                        ref_list.append(ref.toJson())
                    return{
                        "success": True,
                        "referee_list": ref_list
                    }

                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }


    # added checking crew size when assignening referee
    @http.route('/api/organization/assign_referee_to_match', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def assign_referee_to_match(self, **kw):
        _logger.info(
            "###############IN ASSIGN REFEREE TO MATCH######################")
        _logger.info(kw)
        _logger.info(
            "###############IN ASSIGN REFEREE TO MATCH######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        match_id = kw.get("match_id")
        referee_id = kw.get("referee_id")
        try:
            if organization_id and server_token and match_id and referee_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    _match = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)], limit=1)
                    if _match:
                        if _match.event_id.organization_id.id == organization.id:
                            # here we will check for refree crew size before assign
                            # event = request.env["event.event"].sudo().search(
                            #     [('id', '=', match_id.event_id)], limit=1)
                            # if len(_match.referees) == event.crew_size:
                            #     return {
                            #         "success": False,
                            #         "message": "Even restricts more assignement of refreee to this match(check event "
                            #                    "crew size) "
                            #     }
                            ref = request.env["referees.referees"].sudo().search(
                                [('id', '=', referee_id)], limit=1)
                            if ref:
                                ls = []
                                for reff in _match.referees:
                                    ls.append(reff.id)
                                _logger.info(
                                    "##############MATCH REFEREES##################")
                                _logger.info(ls)
                                _logger.info(
                                    "##############MATCH REFEREES##################")
                                if ref.id not in ls:
                                    ls.append(ref.id)
                                    _match.referees = ls
                                    return{
                                        "success": True,
                                        "message": "Referee assigned to match."
                                    }
                                else:
                                    return{
                                        "success": False,
                                        "message": "This referee is already assigned to this match."
                                    }
                            else:
                                return{
                                    "success": False,
                                    "message": "Referee not found."
                                }
                        else:
                            return{
                                "success": False,
                                "message": "This match does not belong to this organization."
                            }
                    else:
                        return{
                            "success": False,
                            "message": "Match not found."
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/get_organization_team', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_organization_team(self, **kw):
        _logger.info(
            "###############IN GET ORGANIZATION TEAM######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET ORGANIZATION TEAM######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        try:
            if organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    teams = request.env["team.team"].sudo().search(
                        [('organization_id', '=', organization.id)])
                    teams_list = []
                    for team in teams:
                        teams_list.append(team.toJson(isToken=True))
                    return {
                        "success": True,
                        "teams_list": teams_list
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/get_organization_match', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_organization_match(self, **kw):
        _logger.info(
            "###############IN GET ORGANIZATION MATCH######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET ORGANIZATION MATCH######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        try:
            if server_token and organization_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    matches = request.env["match.match"].sudo().search([])
                    matches_list = []
                    for mch in matches:
                        if mch.event_id.organization_id.id == organization.id:
                            matches_list.append(mch.toJson(detail=True))
                    return {
                        "success": True,
                        "matches_list": matches_list
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/organization/get_organization_profile', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_organization_profile(self, **kw):
        _logger.info(
            "###############IN GET ORGANIZATION PROFILE######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET ORGANIZATION PROFILE######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        try:
            if server_token and organization_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    return {
                        "success": True,
                        "organization": organization.toJson(token=True)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/update_organization_profile', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def update_organization_profile(self, **kw):
        _logger.info(
            "###############IN UPDATE ORGANIZATION PROFILE######################")
        _logger.info(kw)
        _logger.info(
            "###############IN UPDATE ORGANIZATION PROFILE######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        data = kw.get('data')
        try:
            if server_token and organization_id and data:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    organization.write(data)
                    return {
                        "success": True,
                        "organization": organization.toJson(token=True)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/update_organization_sport_types', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def update_organization_sport_types(self, **kw):
        _logger.info(
            "###############IN UPDATE ORGANIZATION SPORT TYPES######################")
        _logger.info(kw)
        _logger.info(
            "###############IN UPDATE ORGANIZATION SPORT TYPES######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        data = kw.get('data')
        try:
            if server_token and organization_id and data:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    ls = []
                    for sport_type_id in data:
                        if type(sport_type_id) == int:
                            sport_type = request.env['sport.type'].sudo().search(
                                [('id', '=', sport_type_id)])
                            if sport_type:
                                ls.append(sport_type.id)
                    organization.write({
                        "sport_type": ls
                    })
                    return {
                        "success": True,
                        "organization": organization.toJson(token=True)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/get_match_ref_requests', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_match_ref_requests(self, **kw):
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        match_id = kw.get("match_id")
        try:
            if server_token and organization_id and match_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    match = matches = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)])
                    if match:
                        if match.event_id.organization_id.id == organization.id:
                            match_requests = request.env["match.match.referee.requests"].sudo().search(
                                [('match_id', '=', match.id)])
                            match_request_list = []
                            for match_request in match_requests:
                                match_request_list.append(
                                    match_request.toJson())
                            return {
                                "success": True,
                                "match_request_list": match_request_list
                            }
                        else:
                            return {
                                "success": False,
                                "message": "This match does not belong to this organization",
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Match not found",
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    # # here we will display a set of referees for organizations to vet
    # @http.route('/api/organization/get_all_ref', type='json', auth='public', website=True, csrf=False, method=['POST'])
    # def get_all_ref(self, **kw):
    #     _logger.info(
    #         "###############IN GET REF REQUESTS######################")
    #     _logger.info(kw)
    #     _logger.info(
    #         "###############IN GET REF REQUESTS######################")
    #     organization_id = kw.get("organization_id")
    #     server_token = kw.get("server_token")
    #     match_id = kw.get("match_id")
    #     try:
    #         if server_token and organization_id and match_id:
    #             organization = request.env["organization.organization"].sudo().search(
    #                 [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
    #             if organization:
    #                 match = matches = request.env["match.match"].sudo().search(
    #                     [('id', '=', match_id)])
    #                 if match.event_id.vet_or_auto_accept == 'vet':
    #                     referees = request.env["referees.referees"].sudo().search([])
    #                     ref_list = []
    #                     for ref in referees:
    #                         ref_list.append(ref.toJson())
    #                     return {
    #                         "success": True,
    #                         "matches_list": ref_list
    #                     }
    #             else:
    #                 return {
    #                     "success": False,
    #                     "message": "Invalid server token",
    #                     "error_code": 111
    #                 }
    #         else:
    #             return {
    #                 "success": False,
    #                 "message": "All fields are required",
    #                 "error_code": 111
    #             }
    #     except Exception as e:
    #         msg = str(e)
    #         return {
    #             "success": False,
    #             "message": msg
    #         }


    # here we will create a referee request from given referees
    @http.route('/api/organization/request_refereee_from_org', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def request_a_refree(self, **kw):
        _logger.info(
            "###############IN GET Request to refreee from org######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET Request to refreee from org######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        match_id = kw.get("match_id")
        refree_id = kw.get("referee_id")
        try:
            if server_token and organization_id and match_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    match = matches = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)])
                    ref = refs = request.env["referees.referees"].sudo().search(
                        [('id', '=', refree_id)])
                    if match and ref:
                        if ref in match.referees:
                            return {
                                "success": False,
                                "message": "Request failed,ref is already assigned for this match",
                            }
                        else:
                            _logger.info('creating request from organization to refree on a match')
                            ref_req = request.env["organization.match.referee.requests"].sudo().search(
                                [('match_id', '=', match.id), ('referee_id', '=', ref.id)])
                            if ref_req:
                                return {
                                    "success": False,
                                    "message": "Request failed, you already made a request to the following refree",
                                }
                            else:
                                ref_req_create = request.env['organization.match.referee.requests'].create({
                                    'refree_id': refree_id,
                                    'match_id': match_id
                                })
                                if ref_req_create:
                                    return {
                                        "success": True,
                                        "message": "Request sent successfully"
                                    }
                                else:
                                    return {
                                        "success": False,
                                        "message": "Something went wrong, request canceled"
                                    }
                    else:
                        return {
                            "success": False,
                            "message": "Refreee or Match not found",
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required",
                    "error_code": 111
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }


    # added to cehck the crew size before assigning
    @http.route('/api/organization/approve_or_decline_ref_requests', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def approve_or_decline_ref_requests(self, **kw):
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        request_id = kw.get("request_id")
        action = kw.get("action")

        try:
            if organization_id and server_token and request_id and action:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    match_request = request.env["match.match.referee.requests"].sudo().search(
                        [('id', '=', request_id)])
                    if match_request:
                        # # here we will check for refree crew size before before approving
                        # event = request.env["event.event"].sudo().search(
                        #     [('id', '=', match_request.match_id.event_id)], limit=1)
                        # _match = request.env["match.match"].sudo().search(
                        #     [('id', '=', match_request.match_id)], limit=1)
                        # if len(_match.referees) == event.crew_size:
                        #     return {
                        #         "success": False,
                        #         "message": "Even restricts more assignement of refreee to this match(check event "
                        #                    "crew size) "
                        #     }
                        if match_request.match_id.event_id.organization_id.id == organization.id:
                            # if match_request.is_declined or match_request.status:
                            #     return {
                            #         "success": False,
                            #         "message": "Request has already been accepted" if match_request.status else "Request has already been declined"
                            #     }
                            # else:
                            if action == "accept":
                                match_request.write({
                                    "status": True,
                                    "is_declined": False
                                })
                                ls = []
                                for reff in match_request.match_id.referees:
                                    ls.append(reff.id)
                                if match_request.referee_id.id not in ls:
                                    ls.append(match_request.referee_id.id)
                                    match_request.match_id.referees = ls
                                return {
                                    "success": True,
                                    "message": f"Request Approved {match_request.match_id.name}"
                                }
                            elif action == "decline":
                                match_request.write({
                                    "is_declined": True,
                                    "status": False
                                })
                                return {
                                    "success": True,
                                    "message": "Request Declined"
                                }
                            else:
                                return {
                                    "success": False,
                                    "message": "Invalid action value."
                                }
                        else:
                            return {
                                "success": False,
                                "message": "Match does not belong to this organization."
                            }

                    else:
                        return {
                            "success": False,
                            "message": "Request not found."
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/get_chat_messages', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_chat_messages(self, **kw):
        _logger.info(
            "###############IN GET CHAT MESSAGES######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET CHAT MESSAGES######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")

        try:
            if organization_id and server_token:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    def get_partner_id(val):
                        return val.partner_id.id
                    # CLEANR = re.compile(
                    #     '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                    # def cleanhtml(raw_html):
                    #     cleantext = re.sub(CLEANR, '', raw_html)
                    #     return cleantext
                    mail_channels = request.env["mail.channel"].sudo().search(
                        [])
                    org_name = organization.user_id.name
                    channel_ids = []
                    channel_names = []
                    for channel in mail_channels:
                        if org_name in str(channel.name):
                            ls = list(
                                map(get_partner_id, channel.channel_last_seen_partner_ids))
                            _logger.info(ls)
                            _logger.info(
                                organization.user_id.partner_id)
                            if organization.user_id.partner_id.id in ls and len(ls) == 2:
                                channel_ids.append(channel.id)
                                channel_names.append(channel.name)
                                d = {
                                    "name": channel.name,
                                    "active": channel.active,
                                    "channel_type": channel.channel_type,
                                    "is_chat": channel.is_chat,
                                    "description": channel.description,
                                    "email_send": channel.email_send,
                                    "channel_last_seen_partner_ids": channel.channel_last_seen_partner_ids,
                                    "public": channel.public,
                                    "moderator_ids": channel.moderator_ids,
                                    "is_subscribed": channel.is_subscribed,
                                }
                                _logger.info(d)

                    _logger.info(f"CHANNEL ID: {channel_ids}")
                    messages_list = []
                    for i, channel_id in enumerate(channel_ids):
                        messages = request.env["mail.message"].sudo().search(
                            [('channel_ids', '!=', False), ('channel_ids.id', '=', channel_id)], limit=1)
                        for m in messages:
                            # if m.author_id.id == organization.user_id.partner_id.id:
                            _logger.info(f"MESSAGE : {m}")
                            _logger.info(f"CHANNEL ID'S: {m.channel_ids}")
                            _logger.info(f"MESSAGE BODY: {m.body}")
                            messages_list.append({
                                "channel_id": channel_id,
                                "last_message": cleanhtml(m.body),
                                "create_date_time": m.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                                "name": str(channel_names[i]).split(',')[0]
                            })
                    _logger.info(f"MESSAGE LIST: {messages_list}")
                    return{
                        "success": True,
                        "messages_list": messages_list
                    }

                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }

        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/send_channel_chat_messages', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def send_channel_chat_messages(self, **kw):
        _logger.info(
            "###############IN SEND CHANNEL CHAT MESSAGES######################")
        _logger.info(kw)
        _logger.info(
            "###############IN SEND CHANNEL CHAT MESSAGES######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        channel_id = kw.get("channel_id")
        message_content = kw.get("message_content")
        try:
            if organization_id and server_token and channel_id and message_content:
                message_content = str(message_content).strip()
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    channel = request.env['mail.channel'].sudo().search(
                        [('id', '=', channel_id)])
                    _logger.info(channel)
                    _logger.info(channel.name)
                    if channel:
                        msg = channel.message_post(subject="", body=message_content, author_id=organization.user_id.partner_id.id,
                                                   message_type='comment', subtype_id=1)
                        return {
                            "success": True,
                            "time_stamp": msg.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "message": "Message sent."
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Channel not found."
                        }
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }

        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/get_channel_chat_messages', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def get_channel_chat_messages(self, **kw):
        _logger.info(
            "###############IN GET CHANNEL CHAT MESSAGES######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET CHANNEL CHAT MESSAGES######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        channel_id = kw.get("channel_id")
        try:
            if organization_id and server_token and channel_id:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    messages = request.env["mail.message"].sudo().search(
                        [('channel_ids', '!=', False), ('channel_ids.id', '=', channel_id)])
                    messages_list = []
                    for m in messages:
                        messages_list.append({
                            "channel_id": channel_id,
                            "message": cleanhtml(m.body),
                            "create_date_time": m.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "is_sender": m.author_id.id == organization.user_id.partner_id.id
                        })
                    return{
                        "success": True,
                        "messages_list": messages_list
                    }

                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }

        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/send_chat_message', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def send_chat_message(self, **kw):
        _logger.info(
            "###############IN SEND CHAT MESSAGE######################")
        _logger.info(kw)
        _logger.info(
            "###############IN SEND CHAT MESSAGE######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        recipient_detail = kw.get("recipient_detail")
        message = kw.get("message")
        try:
            if organization_id and server_token and recipient_detail and message:
                message = str(message).strip()
                recipient_id = int(recipient_detail.get('id'))
                recipient_type = recipient_detail.get('type')
                if recipient_id and recipient_type:
                    organization = request.env["organization.organization"].sudo().search(
                        [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                    if organization:
                        check_recipient_type = False
                        recipient_user = ""
                        if recipient_type == "referee" or recipient_type == "coach":
                            check_recipient_type = True
                            if recipient_type == "referee":
                                ref = request.env["referees.referees"].sudo().search(
                                    [('id', '=', recipient_id)])
                                if ref:
                                    recipient_user = ref.user_id
                                    if not recipient_user:
                                        return{
                                            "success": False,
                                            "message": "Referee user not found",
                                        }
                                else:
                                    return{
                                        "success": False,
                                        "message": "Referee not found",
                                    }
                            else:
                                coach = request.env["coach.coach"].sudo().search(
                                    [('id', '=', recipient_id)])
                                if coach:
                                    recipient_user = coach.user_id
                                    if not recipient_user:
                                        return{
                                            "success": False,
                                            "message": "Coach user not found",
                                        }
                                else:
                                    return{
                                        "success": False,
                                        "message": "Coach not found",
                                    }
                        channel_id = -1
                        if check_recipient_type:
                            def get_partner_id(val):
                                return val.partner_id.id
                            mail_channels = request.env["mail.channel"].sudo().search([
                            ])
                            org_name = organization.user_id.name
                            _logger.info(mail_channels)

                            for channel in mail_channels:

                                if org_name in str(channel.name) and recipient_user.name in str(channel.name):
                                    ls = list(
                                        map(get_partner_id, channel.channel_last_seen_partner_ids))
                                    _logger.info(ls)
                                    _logger.info(
                                        organization.user_id.partner_id)
                                    _logger.info(recipient_user.partner_id)
                                    if organization.user_id.partner_id.id in ls and recipient_user.partner_id.id in ls and len(ls) == 2:
                                        channel_id = channel.id
                                        d = {
                                            "name": channel.name,
                                            "active": channel.active,
                                            "channel_type": channel.channel_type,
                                            "is_chat": channel.is_chat,
                                            "description": channel.description,
                                            "email_send": channel.email_send,
                                            "channel_last_seen_partner_ids": channel.channel_last_seen_partner_ids,
                                            "public": channel.public,
                                            "moderator_ids": channel.moderator_ids,
                                            "is_subscribed": channel.is_subscribed,
                                        }
                                        _logger.info(d)

                            _logger.info(f"CHANNEL ID: {channel_id}")
                            if channel_id == -1:
                                # TODO CREATE THE CHANNEL HERE
                                pass

                            channel = request.env['mail.channel'].sudo().browse(
                                channel_id)
                            # channel.message_post(subject="", body=message, author_id=organization.user_id.id,
                            #                      message_type='comment', subtype_id=request.env.ref('mail.mt_discussion').id, partner_ids=[recipient_user.partner_id.id])
                            channel.message_post(subject="", body=message, author_id=organization.user_id.partner_id.id,
                                                 message_type='comment', subtype_id=1, partner_ids=[recipient_user.partner_id.id])
                            _logger.info(f"FETCHD CHANNEL: {channel}")

                        else:
                            return{
                                "success": False,
                                "message": "Invalid recipient.",
                            }

                    else:
                        return {
                            "success": False,
                            "message": "Invalid server token",
                            "error_code": 111
                        }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/organization/change_password', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def change_password(self, **kw):
        _logger.info(
            "###############IN CHANGE PASSWORD######################")
        _logger.info(kw)
        _logger.info(
            "###############IN CHANGE PASSWORD######################")
        organization_id = kw.get("organization_id")
        server_token = kw.get("server_token")
        current_password = kw.get("current_password")
        new_password = kw.get("new_password")
        try:
            if organization_id and server_token and current_password and new_password:
                organization = request.env["organization.organization"].sudo().search(
                    [('id', '=', organization_id), ('server_token', '=', server_token)], limit=1)
                if organization:
                    user = organization.user_id.login
                else:
                    return {
                        "success": False,
                        "message": "Invalid server token",
                        "error_code": 111
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required."
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }
