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
from datetime import datetime
import base64
import traceback

_logger = logging.getLogger(__name__)

from math import cos, asin, sqrt, pi


class RefereeController(http.Controller):

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

    def distance(self, lat1, lon1, lat2, lon2):
        p = pi / 180
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))  # 2*R*asin...

    @http.route('/api/referee/get_events', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def get_events(self, **kw):
        try:
            ref_id = kw.get("ref_id")
            server_token = kw.get("server_token")
            referee = request.env["referees.referees"].sudo().search(
                [('id', '=', ref_id), ('server_token', '=', server_token)], limit=1)
            if referee:
                events = request.env["event.event"].sudo().search(
                    [], limit=20, order="id desc")
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

    @http.route('/api/referee/upload_image', type='http', auth='public', website=True, csrf=False, method=['GET'])
    def upload_image(self, **kw):
        _logger.info("##############IN UPLOAD IMAGE##############")
        _logger.info(request.httprequest.files.getlist('image'))
        _logger.info(request.httprequest.files.getlist('file'))
        _logger.info(kw)
        _logger.info("##############IN UPLOAD IMAGE##############")
        ref_id = kw.get("id")
        year_of_experience = kw.get("year_of_experience")
        files = request.httprequest.files.getlist('file')

        try:
            if ref_id and year_of_experience and len(files) > 0:
                # referee = request.env["referees.referees"].sudo().search(
                #         [('id', '=', ref_id), ('server_token', '=', server_token)], limit=1)
                referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', ref_id)], limit=1)
                if referee:
                    attachment = files[0].read()
                    referee.write({
                        "docs": base64.encodebytes(attachment),
                        "year_of_experience": year_of_experience
                    })
                    return json.dumps({
                        "success": True,
                        "message": "Uploaded."
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "message": "Referee not found"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "message": "All fields are required!"
                })
        except Exception as e:
            msg = str(e)
            return json.dumps({
                "success": False,
                "message": msg
            })

    @http.route('/api/referee/get_all_matches', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def get_all_matches(self, **kw):
        _logger.info("##############IN GET ALL MATCHES##############")
        _logger.info(kw)
        _logger.info("##############IN GET ALL MATCHES##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        try:
            if referee_id and server_token:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    matches = request.env["match.match"].sudo().search([])
                    matches_list = []
                    for mch in matches:
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/referee/get_ref_matches', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def get_ref_matches(self, **kw):
        _logger.info("##############IN GET REF MATCHES##############")
        _logger.info(kw)
        _logger.info("##############IN GET REF MATCHES##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        try:
            if referee_id and server_token:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    matches = request.env["match.match"].sudo().search([])
                    matches_list = []
                    for mch in matches:
                        if referee in mch.referees:
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/referee/get_match_detail', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def get_match_detail(self, **kw):
        _logger.info("##############IN GET MATCH DETAIL##############")
        _logger.info(kw)
        _logger.info("##############IN GET MATCH DETAIL##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        match_id = kw.get('match_id')
        try:
            if referee_id and server_token and match_id:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    match = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)], limit=1)
                    if match:
                        return {
                            "success": True,
                            "match": match.toJson(match_detail=True)
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    # added checking to ecents crewsize efore requesting officiating
    @http.route('/api/referee/request_officiating', type='json', auth='public', website=True, csrf=False,
                method=['GET'])
    def request_officiating(self, **kw):
        _logger.info("##############IN REQUEST OFFICIATING##############")
        _logger.info(kw)
        _logger.info("##############IN REQUEST OFFICIATING##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        match_id = kw.get('match_id')

        try:
            if referee_id and server_token and match_id:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    match = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)], limit=1)
                    if match:
                        # event = request.env["event.event"].sudo().search(
                        #     [('id', '=', match.event_id)])
                        # if len(match.referees) == event.crew_size:
                        #     return {
                        #         "success": False,
                        #         "message": "Request failed,Match already reached Crew Size",
                        #     }
                        if referee not in match.referees:
                            match_request = request.env["match.match.referee.requests"].sudo().search(
                                [('match_id', '=', match.id), ('referee_id', '=', referee.id)])
                            if match_request:
                                return {
                                    "success": False,
                                    "message": "Request failed, you already made a request to officiate the match",
                                }
                            else:
                                created_match_request = request.env["match.match.referee.requests"].sudo().create({
                                    "match_id": match.id,
                                    "referee_id": referee.id
                                })
                                if created_match_request:
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
                                "message": "Request failed, you are already an official for this match",
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    # here we will send all requests offers to the referee from organizations
    @http.route('/api/referee/get_match_ref_requests', type='json', auth='public', website=True, csrf=False,
                method=['POST'])
    def get_match_ref_requests(self, **kw):
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET MATCH REF REQUESTS######################")
        referee_id = kw.get("referees")
        server_token = kw.get("server_token")
        match_id = kw.get("match_id")
        try:
            if server_token and referee_id:
                referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    requestss = requestssss = request.env["organization.match.referee.requests"].sudo().search(
                        [('referee_id', '=', referee_id)])
                    if requestss:
                        match_request_list = []
                        for match_request in requestss:
                            match_request_list.append(
                                match_request.toJson())
                        return {
                            "success": True,
                            "match_request_list": match_request_list
                        }
                    else:
                        return {
                            "success": True,
                            "message": "No requests found",
                            "match_request_list": []
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

    # here refe will accept or decline a req from the organizations

    # added to cehck the crew size before assigning
    @http.route('/api/organization/approve_or_decline_ref_requests', type='json', auth='public', website=True,
                csrf=False, method=['POST'])
    def approve_or_decline_org_requests(self, **kw):
        _logger.info(
            "###############IN GET MATCH Org REQUESTS######################")
        _logger.info(kw)
        _logger.info(
            "###############IN GET MATCH ORG REQUESTS######################")
        referee_id = kw.get("referee_id")
        server_token = kw.get("server_token")
        request_id = kw.get("request_id")
        action = kw.get("action")

        try:
            if referee_id and server_token and request_id and action:
                referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    match_request = request.env["organization.match.referee.requests"].sudo().search(
                        [('id', '=', request_id)])
                    if match_request:
                        # here we will check for refree crew size before before approving
                        event = request.env["event.event"].sudo().search(
                            [('id', '=', match_request.match_id.event_id)], limit=1)
                        _match = request.env["match.match"].sudo().search(
                            [('id', '=', match_request.match_id)], limit=1)
                        if len(_match.referees) == event.crew_size:
                            return {
                                "success": False,
                                "message": "Even restricts more assignement of refreee to this match(check event "
                                           "crew size) "
                            }

                        if action == "accept":
                            match_request.write({
                                "status": True,
                                "has_accepted": True
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
                                "has_accepted": False,
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

    @http.route('/api/referee/change_match_status', type='json', auth='public', website=True, csrf=False,
                method=['GET'])
    def change_match_status(self, **kw):
        def get_ref_id(ref):
            return ref.id

        _logger.info("##############IN CHANGE MATCH STATUS##############")
        _logger.info(kw)
        _logger.info("##############IN CHANGE MATCH STATUS##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        match_id = kw.get('match_id')
        status_code = kw.get('status_code')

        try:
            if referee_id and server_token and match_id and status_code:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    match = request.env["match.match"].sudo().search(
                        [('id', '=', match_id)], limit=1)
                    if match:
                        ls = list(map(get_ref_id, match.referees))
                        _logger.info(ls)
                        if referee.id in ls:
                            success = False
                            msg = ""
                            if status_code == "ready":
                                if match.state != "start" and match.state != "end":
                                    match.write({
                                        "state": "ready"
                                    })
                                    success = True
                                    msg = "Match status changed to ready state."
                                else:
                                    success = False
                                    if match.state != "start":
                                        msg = "Match is already ended."
                                    else:
                                        msg = "Match is already started."

                            elif status_code == "start":
                                if match.state != "end":
                                    match.write({
                                        "state": "start"
                                    })
                                    success = True
                                    msg = "Match started"
                                else:
                                    success = False
                                    msg = "Match is already ended."

                            elif status_code == "end":
                                if match.state != "ready":
                                    match.write({
                                        "state": "end"
                                    })
                                    success = True
                                    msg = "Match ended."
                                else:
                                    success = False
                                    msg = "Match can not be ended before it starts."
                            else:
                                success = False
                                msg = f"Invalid state provided, {status_code} state is not allowed"
                            return {
                                "success": success,
                                "message": msg
                            }
                        else:
                            return {
                                "success": False,
                                "message": "You don't have access to this match, status can not be changed.",
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/referee/update_profile', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def update_profile(self, **kw):
        _logger.info("##############IN REFEREE UPDATE PROFILE##############")
        _logger.info(kw)
        _logger.info("##############IN REFEREE UPDATE PROFILE##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        data = kw.get('data')

        try:
            if referee_id and server_token and data:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    referee.write(data)
                    return {
                        "success": True,
                        "message": "Profile updated.",
                        "referee": referee.toJson(token=True)
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/referee/update_sport_types', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def update_sport_types(self, **kw):
        def get_sport_type_id(sport_type):
            return sport_type.id

        _logger.info(
            "##############IN REFEREE UPDATE SPORT TYPE##############")
        _logger.info(kw)
        _logger.info(
            "##############IN REFEREE UPDATE SPORT TYPE##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        data = kw.get('data')

        try:
            if referee_id and server_token and data:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    ls = []
                    for sport_type_id in data:
                        if type(sport_type_id) == int:
                            sport_type = request.env['sport.type'].sudo().search(
                                [('id', '=', sport_type_id)])
                            if sport_type:
                                ls.append(sport_type.id)
                    referee.write({
                        "sport": ls
                    })
                    return {
                        "success": True,
                        "message": "Profile updated.",
                        "referee": referee.toJson(token=True)
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    # here we will fetch the list of events in a certain radius
    @http.route('/api/referee/get_event_in_radius', type='json', auth='public', website=True, csrf=False,
                method=['GET'])
    def update_sport_types(self, **kw):
        _logger.info(
            "##############IN REFEREE EVENT RADIUS##############")
        _logger.info(kw)
        _logger.info(
            "##############IN REFEREE EVENT RADIUS##############")
        referee_id = kw.get('referee_id')
        server_token = kw.get('server_token')
        data = kw.get('data')
        try:
            if referee_id and server_token and data:
                referee = referee = request.env["referees.referees"].sudo().search(
                    [('id', '=', referee_id), ('server_token', '=', server_token)], limit=1)
                if referee:
                    events = request.env['event.event'].sudo().search([])
                    events_list = []
                    for eve in events:
                        dis = self.distance(eve.location.lat, eve.location.lon, referee.location.lat,
                                            referee.location.lon)
                        if dis <= referee.radius:
                            events_list.append(eve.toJson())
                    return {
                        'success': True,
                        'event_list': events_list
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
                    "message": "All fields are required!"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }
