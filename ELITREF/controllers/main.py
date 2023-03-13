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


def serializeModel(obj, fileds=None):
    _logger.info("###############GETTING FIELDS###########")
    _logger.info(obj.name)
    _logger.info(obj.__getattribute__)
    # _logger.info(inspect.getmembers(obj))
    members = inspect.getmembers(obj)
    fields = []
    for member in fields:
        _logger.info(fields)
        if hasattr(obj, member):
            fields.append(member)
    _logger.info(fields)
    # _logger.info(obj.iteritems())
    # for key,field in obj.iteritems():
    #     _logger.info(field)


class ApiController(http.Controller):

    @http.route('/api/test_serializer', type='json', auth='none')
    def test_suite(self, mod=None, **kwargs):
        _logger.info("##############IN CONTROLLER##############")
        # dbRes = request.env['coach.coach'].search([])
        # _logger.info(dbRes)
        # serializeModel(dbRes[0])
        # user = request.env["res.users"].sudo().search([('id', '=', 12)])
        # _logger.info(user)
        # _logger.info(user.username)
        # users = {}
        # username = 'Brent' # The users username
        # password = 'mypassword' # The users password

        # salt = os.urandom(32) # A new salt for this user
        # key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        # users[username] = { # Store the salt and key
        #     'salt': salt,
        #     'key': key
        # }
        # salt = users[username]['salt']
        # key = users[username]['key']
        # new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        # _logger.info(key == new_key)
        _logger.info("##############SEARCHING##############")
        # _logger.info(self.create_or_get('res.country', ['name'], ['Utopia'], vals={"name":"Utopia"}, create=True))
        dbRes = request.env['match.match'].search([])
        _logger.info(dbRes[0])
        # _logger.info(dbRes[0].toJson())
        # pwd = dbRes[0].password
        # salt = pwd[:32] # 32 is the length of the salt
        # key = pwd[32:]
        # new_key = hashlib.pbkdf2_hmac(
        #     'sha256',
        #     "123456".encode('utf-8'), # Convert the password to bytes
        #     salt,
        #     100000
        # )
        # _logger.info(dbRes[0].user_id._check_credentials('123456', {'interactive':False}))
        # _logger.info(dbRes[0].user_id._login(request.env, 'res.users', 'login', ))
        # _logger.info(request.session.authenticate('Tes', dbRes[0].user_id.login, "123455166"))
        _logger.info("##############IN CONTROLLER##############")
        return {
            "success": True,
            "match": dbRes[0].toJson()
        }

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

    def getBool(self, val):
        if val == "true":
            return True
        return False

    @http.route('/api/login', type='json', auth='none')
    def login(self, mod=None, **kwargs):
        username = kwargs.get("email")
        password = kwargs.get("password")
        login_type = kwargs.get("login_type")
        models = ["organization.organization",
                  "referees.referees", "coach.coach", "fans.fans"]
        names = ["organization", "referee", "coach", "fan"]
        userdd = request.env["res.users"].sudo().search([], limit=1)
        chchchch = request.session.uid
        sisisisi = request.session
        try:
            if username and password:
                # username = str(username).strip()
                user = request.env["res.users"].sudo().search(
                    [('login', '=', username)], limit=1)
                _logger.info("##############LOGIN##############")
                _logger.info(user)
                _logger.info("##############LOGIN##############")
                if user:
                    logged_in_user = request.session.authenticate(
                        request.env.cr.dbname, username, f"{password}")
                    _logger.info(logged_in_user)
                    logged_in_user_type = request.env[f"{models[login_type - 1]}"].sudo().search(
                        [('user_id', '=', logged_in_user)], limit=1)
                    if logged_in_user_type:
                        _logger.info(logged_in_user_type)
                        letters = string.ascii_letters
                        result_str = ''.join(random.choice(letters)
                                             for i in range(30))
                        logged_in_user_type.server_token = result_str
                        return {
                            "success": True,
                            "message": "Login successful",
                            f"{names[login_type - 1]}": logged_in_user_type.toJson(token=True)
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Authorization failed"
                        }
                else:
                    return {
                        "success": False,
                        "message": "User not found"
                    }
            else:
                return {
                    "success": False,
                    "message": "username and password required."
                }
        except AccessDenied:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    @http.route('/api/get_states', type='json', auth='none')
    def get_states(self, mod=None, **kwargs):
        states = request.env["res.country.state"].sudo().search(
            [('country_id', '=', 233)])
        try:
            if states:
                result = []
                for state in states:
                    result.append({
                        "id": state.id,
                        "name": state.name,
                        "code": state.code,
                        "country_id": state.country_id.id
                    })
                return {
                    "success": True,
                    "states": result
                }
            else:
                return {
                    "success": False,
                    "message": "Something went wrong. Unable to fetch states."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong. Unable to fetch states."
            }

    @http.route('/api/get_preference_types', type='json', auth='none')
    def get_preference_types(self, mod=None, **kwargs):
        prefs = request.env["referees.referees.preferences.type"].sudo().search([
        ])
        try:
            if prefs:
                pref_list = []
                for pref in prefs:
                    pref_list.append(pref.toJson())

                return {
                    "success": True,
                    "preference_types": pref_list
                }
            else:
                return {
                    "success": False,
                    "message": "Something went wrong. Unable to fetch preference types."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong. Unable to fetch preference types."
            }

    @http.route('/api/get_field_types', type='json', auth='none')
    def get_field_types(self, mod=None, **kwargs):
        field_types = request.env["event.court.types"].sudo().search([])
        try:
            if field_types:
                filed_type_list = []
                for pref in field_types:
                    filed_type_list.append(pref.toJson())

                return {
                    "success": True,
                    "field_types": filed_type_list
                }
            else:
                return {
                    "success": False,
                    "message": "Something went wrong. Unable to fetch field types."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong. Unable to fetch field types."
            }

    @http.route('/api/set_sport_types', type='json', auth='none')
    def set_sport_types(self, mod=None, **kwargs):
        try:
            sport_types = kwargs.get("sport_types")
            if sport_types:
                _logger.info("####### CREATING ################")
                _logger.info(sport_types)
                _logger.info(type(sport_types))
                _logger.info("####### CREATING ################")
                for i, sport_type in enumerate(list(sport_types)):
                    # request.env["sport.type"].sudo().create({"name":f"{sport_type}"})
                    self.create_or_get("sport.type", ['name'], [f"{sport_type}"],
                                       vals={"name": f"{sport_type}"}, create=True)

                return {
                    "success": True,
                    "message": "Sport types created."
                }
            else:
                return {
                    "success": False,
                    "message": "Can not create sport types."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong. Unable to fetch preference types."
            }

    @http.route('/api/get_sport_types', type='json', auth='none')
    def get_sport_types(self, mod=None, **kwargs):
        sport_types = request.env["sport.type"].sudo().search([])
        try:
            if sport_types:
                sport_type_list = []
                for sport_type in sport_types:
                    sport_type_list.append(sport_type.toJson())

                return {
                    "success": True,
                    "sport_types": sport_type_list
                }
            else:
                return {
                    "success": False,
                    "message": "Something went wrong. Unable to fetch preference types."
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong. Unable to fetch preference types."
            }

    @http.route('/api/create_organization', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_organization(self, **kw):
        try:
            _logger.info("##############IN ORGANIZATION##############")
            _logger.info(kw)
            _logger.info("##############IN ORGANIZATION##############")
            if kw.get("user").get('name') and kw.get("user").get('email') and kw.get("user").get('password') and kw.get('user').get('login'):
                passwd = kw.get("user").get('password')
                state = kw.get("state")
                sport_types = kw.get("sport_types")
                organization_data = kw.get("organization")
                # salt = os.urandom(32) # A new salt for this user
                # key = hashlib.pbkdf2_hmac('sha256', passwd.encode('utf-8'), salt, 100000)
                # p = str(salt).encode('utf-8') + key
                # _logger.info(f"TYPE: {type(p)}")
                # organization_data['password'] = p.decode('utf-8', 'ignore')
                user = request.env["res.users"].sudo().search(
                    [('login', '=', kw.get("user").get("login"))])
                if not user:
                    dbstate = request.env["res.country.state"].sudo().search(
                        [('name', '=', state['name'])])
                    if dbstate:
                        organization_data['states'] = dbstate[0].id
                        _logger.info(f"STATE: {dbstate}")
                    else:
                        created_state = request.env["res.country.state"].sudo().create(
                            state)
                        organization_data['states'] = created_state.id

                    added_sport_type = []
                    for sport_type in sport_types:
                        sp = self.create_or_get('sport.type', ['name'], [f"{sport_type['name']}"], vals={
                            "name": sport_type['name']
                        }, create=True)
                        added_sport_type.append(sp)
                    organization_data['sport_type'] = added_sport_type

                    # dbsport_type = request.env["sport.type"].sudo().search([('name', '=', sport_type)])
                    # if dbsport_type:
                    #     organization_data['sport_type'] = dbsport_type[0].id
                    #     _logger.info(f"SPORT TYPE: {dbsport_type}")
                    # else:
                    #     created_sport_type = request.env["sport.type"].sudo().create({"name": sport_type})
                    # locations = kw.get('locations')
                    # addedLocations = []
                    # for loc in locations:
                    #     country = loc['country']
                    #     country_id = self.create_or_get("res.country", ['name'], [f"{country['name']}"], vals={"name":f"{country['name']}"}, create=True)
                    #     state = loc['state']
                    #     vals = state
                    #     vals['country_id'] = country_id
                    #     state_id = self.create_or_get("res.country.state", ['name'], [f"{state['name']}"], vals=vals, create=True)
                    #     created_location = request.env["location.location"].sudo().create({
                    #         "country":country_id,
                    #         "state":state_id,
                    #         "name":loc['name'],
                    #         "long": loc['long'],
                    #         "lat": loc['lat']
                    #     })
                    #     addedLocations.append(created_location.id)

                    # salt = organization_data['password'][:32] # 32 is the length of the salt
                    # key = organization_data['password'][32:]
                    # new_key = hashlib.pbkdf2_hmac(
                    #     'sha256',
                    #     kw.get("user").get('password').encode('utf-8'), # Convert the password to bytes
                    #     salt,
                    #     100000
                    # )
                    # organization_data['location'] = addedLocations
                    user = request.env["res.users"].sudo().create(
                        kw.get("user"))
                    organization_data['user_id'] = user.id
                    _logger.info(organization_data)
                    organization = request.env["organization.organization"].sudo().create(
                        organization_data)
                    # _logger.info(user)
                    if organization:
                        default_home_team = request.env["team.team"].sudo().create({
                            "name": f"{organization.id}-Home Team",
                            "organization_id": organization.id,
                        })
                        default_away_team = request.env["team.team"].sudo().create({
                            "name": f"{organization.id}-Away Team",
                            "organization_id": organization.id,
                        })
                        organization.default_home_team = default_home_team.id
                        organization.default_away_team = default_away_team.id

                        return {
                            "success": True,
                            "message": "Successfully registered please login."
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                else:
                    return {
                        "success": False,
                        "message": "Email already taken."
                    }
            else:
                return {
                    "success": False,
                    "message": "All fields are required"
                }
        except:
            return {
                "success": False,
                "message": "Something went wrong"
            }

    @http.route('/api/create_referees', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_referees(self, **kw):
        _logger.info("############## create Referees ##############")
        _logger.info(kw)
        try:
            if kw.get("user").get('name') and kw.get("user").get('email') and kw.get("user").get('password') and kw.get(
                    "user").get('login'):
                location = kw.get("location")
                country = location.get("country")
                state = location.get("state")
                sport_type = kw.get("sport_type")
                referees_data = kw.get("referee")
                preference_list = kw.get("preference_list")

                user = request.env["res.users"].sudo().search(
                    [('login', '=', kw.get("user").get("email"))])
                if not user:
                    referees_data['is_radius_set'] = self.getBool(
                        referees_data['is_radius_set'])
                    referees_data['is_minimum_pay_per_game_set'] = self.getBool(
                        referees_data['is_minimum_pay_per_game_set'])
                    referees_data['is_minimum_game_set'] = self.getBool(
                        referees_data['is_minimum_game_set'])
                    referees_data['is_uniform_requirement_set'] = self.getBool(
                        referees_data['is_uniform_requirement_set'])
                    referees_data['uniform_requirement'] = self.getBool(
                        referees_data['uniform_requirement'])
                    referees_data['is_age_group_set'] = self.getBool(
                        referees_data['is_age_group_set'])
                    referees_data['is_competition_level_set'] = self.getBool(
                        referees_data['is_competition_level_set'])

                    added_pref_list = []
                    for preference in preference_list:
                        pref_type = self.create_or_get('referees.referees.preferences.type', ['name'],
                                                       [f"{preference['name']}"], vals={
                                "name": f"{preference['name']}"
                            }, create=True)
                        created_preference = request.env["referees.referees.preferences"].sudo().create({
                            "preference_type": pref_type,
                            "preference_value": preference['value']
                        })
                        added_pref_list.append(created_preference.id)
                    referees_data['preference_list'] = added_pref_list

                    country_id = self.create_or_get("res.country", ['name'], [f"{country['name']}"],
                                                    vals={"name": f"{country['name']}"}, create=True)
                    vals = state
                    vals['country_id'] = country_id
                    state_id = self.create_or_get("res.country.state", ['name'], [
                        f"{state['name']}"], vals=vals, create=True)
                    # created_location = request.env["location.location"].sudo().create({
                    #     "country": country_id,
                    #     "state": state_id,
                    #     "name": location['name'],
                    #     "long": location['long'],
                    #     "lat": location['lat']
                    # })
                    # referees_data['location'] = created_location.id
                    referees_data['country'] = country_id
                    referees_data['states'] = state_id

                    added_sport_type_list = []
                    for sport_t in sport_type:
                        sport_type_id = self.create_or_get('sport.type', ['name'], [f"{sport_t['name']}"], vals={
                            "name": f"{sport_t['name']}"
                        }, create=True)
                        added_sport_type_list.append(sport_type_id)
                    referees_data['sport'] = added_sport_type_list

                    user = request.env["res.users"].sudo().create(
                        kw.get("user"))
                    referees_data['user_id'] = user.id
                    referees_data['name'] = kw.get("user").get('name')
                    referees_data['phone'] = kw.get("user").get('phone')
                    _logger.info(referees_data)
                    referee = request.env["referees.referees"].sudo().create(
                        referees_data)
                    _logger.info(user)
                    _logger.info(referee)
                    if referee:
                        return {
                            "success": True,
                            "message": "Successfully registered please upload your document to continue.",
                            "referee": {
                                "id": referee.id,
                                "server_token": referee.server_token
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                else:
                    return {
                        "success": False,
                        "message": "Username already taken."
                    }
            else:
                return {
                    "success": False,
                    "message": "Please enter all the fields"
                }
        except Exception as e:
            msg = str(e)
            return {
                "success": False,
                "message": msg
            }

    # Registering Fans
    # http://127.0.0.1:8069/api/create_fans

    #
    #      Json Body
    #
    # {
    #     {
    #     "params": {
    #         "user": {
    #             "name": "Fan One",
    #             "email": "fanone@gmail.com",
    #             "login": "fanone",
    #             "password": "123456"
    #         },
    #         "fan": {
    #             "name": "Fan One",
    #             "phone": "Fan phone"
    #         },
    #         "country": {
    #             "name": "Utopia",
    #             "currency_id": "ETB",
    #             "code": "code",
    #             "phone_code": "+251"
    #         },
    #         "state": {
    #             "name": "Dembecha",
    #             "code": "+251"
    #         }
    #     }
    # }

    @http.route('/api/create_fans', type='json', auth='public', website=True, csrf=False, method=['POST'])
    def create_fans(self, **kw):
        _logger.info("**************** create Fans ****************")
        _logger.info(kw)
        if kw.get("user").get('name') and kw.get("user").get('email') and kw.get("user").get('password') and kw.get(
                "user").get('login'):

            country = kw.get("country")
            state = kw.get("state")
            user = kw.get("user")
            username = user.get("login")
            email = user.get("email")
            fans_data = kw.get("fan")

            try:
                user = request.env["res.users"].sudo().search([('login', '=', username), ('email', '=', email)],
                                                              limit=1)
                if user:
                    return {
                        "success": False,
                        "message": "The username already exist"
                    }
                else:
                    country_id = self.create_or_get("res.country", ['name'], [f"{country['name']}"],
                                                    vals={"name": f"{country['name']}"}, create=True)

                    state_id = self.create_or_get('res.country.state', ['name'], [f"{state['name']}"],
                                                  vals={
                                                      "name": f"{state['name']}",
                                                      "code": f"{state['code']}",
                                                      "country_id": country_id
                                                  }, create=True)

                    fans_data['state'] = state_id
                    user = request.env["res.users"].sudo().create(
                        kw.get("user"))
                    fans_data['user_id'] = user.id
                    _logger.info(fans_data)
                    fans = request.env["fans.fans"].sudo().create(fans_data)

                    _logger.info(fans)
                    if fans:
                        return {
                            "success": True,
                            "message": "Registered succesfully, please login."
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
            except:
                return {
                    "success": False,
                    "message": "Somethings wrong"
                }

        else:
            return {
                "success": False,
                "message": "All fields are required."
            }
