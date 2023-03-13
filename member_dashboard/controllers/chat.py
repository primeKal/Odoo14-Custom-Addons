from odoo import http
from odoo.http import request
from ctypes import sizeof
from http import client
import base64
# import babel.messages.pofile
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

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata
class Chat(http.Controller):
    
   @http.route('/my_message', type='http', auth='public', website=True)
   def messages_details(self , **kwargs):
       logged_user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
       message_details = request.env['mail.message'].sudo().search([('author_id', '=', logged_user.partner_id.id)])
       return  request.render('membership.messages_page', {'my_details': message_details})