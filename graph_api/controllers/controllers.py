from calendar import month
from itertools import count

from dateutil import parser

from odoo.exceptions import UserError
import odoo
from odoo.http import route, request
from odoo import http
import random
import json
from datetime import datetime, timedelta, timezone

quater1 = ['January', 'February', 'March']
quater2 = ['April', 'May', 'June']
quater3 = ['July', 'August', 'September']
quater4 = ['October', 'November', 'December']


# model_list = [('Sale', 'Sale'), ('Invoice', 'Invoice'), ('Contacts', 'Contacts')] #list of defined models, imported in ir_models.py

class MyController(odoo.http.Controller):
    @route('/get/hrjobs', auth='public')
    def handler(self):
        jobs = request.env['sale.order'].sudo().search([]).read_group(groupby=['create_date:month'], domain=[],
                                                                      fields=['create_date'])
        jobs = random.sample(request.env['hr.job'].sudo().search([]), k=3)
        return_str = ""
        for j in jobs:
            desc = j.description.replace('\n', '<br/>')
            return_str = return_str + f"""<div class="row-tag col-lg-4 text-center">
            <img alt="client" class="rounded-circle" src="/hr_recruitment/static/description/icon.png"/>
            <h3><p class="hrjob_name">{j.name}</p></h3>
            <p class="hrjob_desc">{desc}</p>
            <button class="hrjob_applynow">Apply Now</button>
            </div>"""
        return return_str


class Models(odoo.http.Controller):
    @route('/get/models', auth='public', type='json')
    def handler(self):
        models = request.env['custom.models'].sudo().search([])
        return_str = {
            "models": {
            }
        }

        # for i in models:
        #     string_list = str(i.string_value).replace(" ", "").split(",")

        #     return_str['models'][i.name.name.replace(" ", "")] = string_list
        return_str = {'models': [{'name': x.name.name, 'id': x.name.id} for x in models]}
        return_str = {'models': [x.name.name for x in models]}

        print("Models ---- : ", models)
        print("return Models ---- : ", return_str)

        return_json = json.dumps(return_str)

        return return_json


class GraphSettings(odoo.http.Controller):
    @route('/save', auth='public', type='json')
    def handler(self):
        res_config = http.request.env['res.config.settings']
        params = request.env['ir.config_parameter'].sudo()
        send_mail = params.get_param('graph_api.graph_model')

        data = request.jsonrequest
        dd = data['params']['data']
        tool = dd['tool']
        if tool == 'sum':
            model_data = request.env['ir.model'].sudo().search([('name', '=', dd['model'])])
            model_data = request.env[model_data.model].sudo().search([])
            if type(getattr(model_data[0], dd['field'])) not in [int, float]:
                print('incorrect combination of data')
                raise UserError('Incorrect combination of sum and attribute, ignoring chart ')

        params.set_param('graph_api.graph_model', value=dd['model'])
        params.set_param('graph_api.graph_frequency', value=dd['fre'])
        params.set_param('graph_api.graph_days', value=dd['days'])
        params.set_param('graph_api.graph_tool', value=dd['tool'])
        params.set_param('graph_api.graph_field', value=dd['field'])
        print(params.get_param('graph_api.graph_model'))
        print(params.get_param('graph_api.graph_frequency'))
        print(params.get_param('graph_api.graph_days'))
        print(params.get_param('graph_api.graph_tool'))
        return True

    @route('/get_fields', auth='public', type='json')
    def handled(self):
        res_config = http.request.env['res.config.settings']
        params = request.env['ir.config_parameter'].sudo()
        send_mail = params.get_param('graph_api.graph_model')

        data = request.jsonrequest
        dd = data['params']['data']
        model_data = request.env['custom.models'].sudo().search([('name', '=', dd)])
        arry_data = []
        for x in model_data.fields:
            arry_data.append(x.name)
        return arry_data

    @route('/getting_data', auth='public', type='json')
    def handling(self):
        params = request.env['ir.config_parameter'].sudo()
        print(params.get_param('graph_api.graph_model'))
        print(params.get_param('graph_api.graph_frequency'))
        print(params.get_param('graph_api.graph_days'))
        print(params.get_param('graph_api.graph_field'))
        model = params.get_param('graph_api.graph_model')
        frequency = params.get_param('graph_api.graph_frequency')
        days = params.get_param('graph_api.graph_days')
        tool = params.get_param('graph_api.graph_tool')
        field = params.get_param('graph_api.graph_field')
        least_date = (datetime.now() - timedelta(days=int(days))).strftime(r'%Y-%m-%d 23:59:59')
        today = datetime.now().strftime(r'%Y-%m-%d 23:59:59')
        print("least date------------", least_date)
        print("Today------------", today)
        print('model: ', model)

        model_data = request.env['ir.model'].sudo().search([('name', '=', model)])

        this_yr = today
        model_records = request.env[model_data.model].sudo().search(
            [('create_date', '>=', least_date), ('create_date', '<=', today)], order='create_date asc')
        model_records = list(model_records)
        for x in model_records:
            if not x[field]:
                model_records.remove(x)
        lazy = False
        new = field
        # model_records.sort(key=lambda x: x.create_date)
        # dont cont if not value is given
        # if tool == 'unique':
        #     lazy = True
            # new_list = []
            # unique_list = []
            # # rremove duplicated values
            # for dictionary in model_records:
            #     if dictionary[field] not in unique_list:
            #         unique_list.append(dictionary[field])
            #         new_list.append(dictionary)
            #
            # print(model_records)
            # model_records = new_list

        # if frequency == 'quarterly':
        #     hor_dates = ['2022-01-01 00:00:00', '2022-05-01 00:00:00', 'Quarter 3', 'Quarter 4']
        #     for mode in model_records:
        #         dto = mode.create_date
        #         dto = datetime(dto.year, dto.month, 1, 0, 0, 0)
        #         # create_date = datetime.strptime(dto, "%Y-%m-%d %H:%M:%S")
        #         if not dto:
        #             continue
        #         iso = dto.isocalendar()
        #         month_count = dto.strftime('%B')
        #         print(month_count)
        #         if month_count in quater1:
        #             ver_count[0] = ver_count[0] + 1
        #             hor_dates[0] = dto
        #         elif month_count in quater2:
        #             ver_count[1] = ver_count[1] + 1
        #             hor_dates[1] = dto
        #         elif month_count in quater3:
        #             ver_count[2] = ver_count[2] + 1
        #             hor_dates[2] = dto
        #         elif month_count in quater4:
        #             ver_count[3] = ver_count[3] + 1
        #             hor_dates[3] = dto
        #     return {
        #         'hor': hor_dates,
        #         'ver': ver_count,
        #         'x_param': 'quarter',
        #         'title': 'Charts Report for ' + str(model),
        #         'descr': 'Showing results of this Year'
        #     }
        if frequency == 'daily':
            if tool == 'sum':
                new = str(field) + ':sum'
            model_records = request.env[model_data.model].sudo().search(
                [], order='create_date asc') \
                .read_group(
                domain=[(field, '!=', False), ('create_date', '>=', least_date), ('create_date', '<=', today)],
                groupby=['create_date:day'], fields=[new], lazy=lazy)
            hor = []
            ver = []
            for i in model_records:
                print(i)
                if tool == 'sum':
                    ver.append(i[field])
                    date_str = i['create_date:day']
                    date = parser.parse(date_str)
                    hor.append(date)
                    continue
                date_str = i['create_date:day']
                date = parser.parse(date_str)
                ver.append(i['__count'])
                hor.append(date)
            #     dto = i.create_date
            #     print(dto)
            #     dto = datetime(dto.year, dto.month, dto.day, 0, 0, 0)
            #     print(dto)
            #     if len(hor) == 0:
            #         hor.append(dto)
            #         if tool == 'sum':
            #             ver.append(i[field])
            #         else:
            #             ver.append(1)
            #     else:
            #         index = 0
            #         flag = False
            #         for x in hor.copy():
            #             if x.month == dto.month and x.day == dto.day:
            #                 if tool == 'sum':
            #                     ver[index] = ver[index] + i[field]
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #                 else:
            #                     ver[index] = ver[index] + 1
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #             index += 1
            #         if not flag:
            #             # dtos =dto.strftime(r'%m/%d/%Y, %H:%M:%S')
            #             hor.append(dto)
            #             if tool == 'sum':
            #                 ver.append(i[field])
            #             else:
            #                 ver.append(1)
            #             print('new data found', str(dto))
            #
            # print('final')
            # print(hor)
            # print(ver)
            return {
                'hor': list(hor),
                'ver': ver,
                'x_param': 'day',
                'title': 'Charts Report for' + str(model),
                'descr': 'Showing results of -- ' + str(model) + '--' + str(frequency) + '--' + str(days) + '--' + str(
                    tool)
            }
        elif frequency == 'monthly':
            if tool == 'sum':
                new = str(field) + ':sum'
            model_records = request.env[model_data.model].sudo().search([], order='create_date asc') \
                .read_group(
                domain=[(field, '!=', False), ('create_date', '>=', least_date), ('create_date', '<=', today)],
                groupby=['create_date:month'], fields=[field], lazy=lazy)
            hor = []
            ver = []
            for i in model_records:
                print(i)
                if tool == 'sum':
                    ver.append(i[field])
                    date_str = i['create_date:month']
                    date = parser.parse(date_str)
                    dto = datetime(date.year, date.month, 1, 0, 0, 0)
                    hor.append(dto)
                    continue
                date_str = i['create_date:month']
                date = parser.parse(date_str)
                dto = datetime(date.year, date.month, 1, 0, 0, 0)
                ver.append(i['__count'])
                hor.append(dto)
            # hor = []
            # ver = []
            # for i in model_records:
            #     dto = i.create_date
            #     dto = datetime(dto.year, dto.month, 1, 0, 0, 0)
            #     if len(hor) == 0:
            #         hor.append(dto)
            #         if tool == 'sum':
            #             ver.append(i[field])
            #         else:
            #             ver.append(1)
            #     else:
            #         index = 0
            #         flag = False
            #         for x in hor.copy():
            #             if x.month == dto.month:
            #                 if tool == 'sum':
            #                     ver[index] = ver[index] + i[field]
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #                 else:
            #                     ver[index] = ver[index] + 1
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #             index += 1
            #         if not flag:
            #             # dtos =dto.strftime(r'%m/%d/%Y, %H:%M:%S')
            #             hor.append(dto)
            #             if tool == 'sum':
            #                 ver.append(i[field])
            #             else:
            #                 ver.append(1)
            #             print('new data found', str(dto))

            return {
                'hor': list(hor),
                'ver': ver,
                'x_param': 'month',
                'title': 'Charts Report for' + str(model),
                'descr': 'Showing results of -- ' + str(model) + '--' + str(frequency) + '--' + str(days) + '--' + str(
                    tool)
            }
        elif frequency == 'weekly':
            if tool == 'sum':
                new = str(field) + ':sum'
            model_records = request.env[model_data.model].sudo().search([], order='create_date asc') \
                .read_group(
                domain=[(field, '!=', False), ('create_date', '>=', least_date), ('create_date', '<=', today)],
                groupby=['create_date:week'], fields=[field], lazy=lazy)
            hor = []
            ver = []
            for i in model_records:
                print(i)
                if tool == 'sum':
                    ver.append(i[field])
                    date_str = i['__domain'][3][2]
                    date = parser.parse(date_str)
                    dto = datetime(date.year, date.month, 1, 0, 0, 0)
                    hor.append(dto)
                    continue
                date_str = i['__domain'][3][2]
                date = parser.parse(date_str)

                dto = datetime(date.year, date.month, date.day, 0, 0, 0)
                ver.append(i['__count'])
                hor.append(dto)
            # hor = []
            # ver = []
            # for i in model_records:
            #     dto = i.create_date
            #     dto = datetime(dto.year, dto.month, 1, 0, 0, 0)
            #     if len(hor) == 0:
            #         hor.append(dto)
            #         if tool == 'sum':
            #             ver.append(i[field])
            #         else:
            #             ver.append(1)
            #     else:
            #         index = 0
            #         flag = False
            #         for x in hor.copy():
            #             if x.month == dto.month:
            #                 if tool == 'sum':
            #                     ver[index] = ver[index] + i[field]
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #                 else:
            #                     ver[index] = ver[index] + 1
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #             index += 1
            #         if not flag:
            #             # dtos =dto.strftime(r'%m/%d/%Y, %H:%M:%S')
            #             hor.append(dto)
            #             if tool == 'sum':
            #                 ver.append(i[field])
            #             else:
            #                 ver.append(1)
            #             print('new data found', str(dto))

            return {
                'hor': list(hor),
                'ver': ver,
                'x_param': 'week',
                'title': 'Charts Report for' + str(model),
                'descr': 'Showing results of -- ' + str(model) + '--' + str(frequency) + '--' + str(days) + '--' + str(
                    tool)
            }

        elif frequency == 'yearly':
            if tool == 'sum':
                new = str(field) + ':sum'
            model_records = request.env[model_data.model].sudo().search(
                [], order='create_date asc') \
                .read_group(
                domain=[(field, '!=', False), ('create_date', '>=', least_date), ('create_date', '<=', today)],
                groupby=['create_date:year'], fields=[new])
            hor = []
            ver = []
            for i in model_records:
                print(i)
                if tool == 'sum':
                    ver.append(i[field])
                    date_str = i['create_date:year']

                    date = parser.parse(date_str)
                    dto = datetime(date.year, 1, 1, 0, 0, 0)
                    hor.append(dto)
                    continue
                date_str = i['create_date:year']
                date = parser.parse(date_str)
                dto = datetime(date.year, 1, 1, 0, 0, 0)
                ver.append(i['__count'])
                hor.append(dto)
            # hor = []
            # ver = []
            # for i in model_records:
            #     dto = i.create_date
            #     dto = datetime(dto.year, 1, 1, 0, 0, 0)
            #     if len(hor) == 0:
            #         hor.append(dto)
            #         if tool == 'sum':
            #             ver.append(i[field])
            #         else:
            #             ver.append(1)
            #     else:
            #         index = 0
            #         flag = False
            #         for x in hor.copy():
            #             if x.year == dto.year:
            #                 if tool == 'sum':
            #                     ver[index] = ver[index] + i[field]
            #                     print('adding count here for verext ', ver[index], 'by', i[field])
            #                     flag = True
            #                 else:
            #                     ver[index] = ver[index] + 1
            #                     print('adding count here for verext ', str(index))
            #                     flag = True
            #             index += 1
            #         if not flag:
            #             # dtos =dto.strftime(r'%m/%d/%Y, %H:%M:%S')
            #             hor.append(dto)
            #             if tool == 'sum':
            #                 ver.append(i[field])
            #             else:
            #                 ver.append(1)
            #             print('new data found', str(dto))
            return {
                'hor': list(hor),
                'ver': ver,
                'x_param': 'year',
                'title': 'Charts Report for' + str(model),
                'descr': 'Showing results of -- ' + str(model) + '--' + str(frequency) + '--' + str(days) + '--' + str(
                    tool)
            }


class CommonController(odoo.http.Controller):
    @route('/get/<model>/<days>', auth='public')
    def handler(self, model, days):
        least_date = (datetime.now() - timedelta(days=int(days))).strftime(r'%Y-%m-%d 23:59:59')
        today = datetime.now().strftime(r'%Y-%m-%d 23:59:59')
        print("least date------------", least_date)
        print("Today------------", today)
        print('model: ', model)
        return_str = {}

        models = request.env['custom.models'].sudo().search([
            ('name', '=', model)])
        # for model in models:
        model = models[0]
        # if i.name.name.replace(" ", "") == model:
        # fetch all field functions
        fieldFunctions = []

        if model.string_value:
            fieldFunctions = model.string_value.replace(" ", "").split(",")

        # always add create_date field to show count on graph
        # if "count(create_date)" not in fieldFunctions:
        #     fieldFunctions.append("count(create_date)")

        model_records = request.env[model.name.model].sudo().search(
            [('create_date', '>=', least_date), ('create_date', '<=', today)])
        mod = model.name.model

        createDict(mod, model_records, fieldFunctions, return_str)

        print("Models ---- : ", models)
        print("return Models ---- : ", return_str)

        return_json = json.dumps(return_str)

        return return_json


def createDict(mod, model_records, fieldFunctions, return_str):
    for i in model_records:
        dto = i.create_date
        if not dto:
            continue
        iso = dto.isocalendar()
        day_count = str(dto.strftime(r'%d/%m/%Y'))
        year_count = str(iso[0])
        week_count = str(iso[1]) + " " + year_count
        month_count = dto.strftime('%B')
        quarter_count = None
        if month_count in quater1:
            quarter_count = '1st Quater ' + year_count
        elif month_count in quater2:
            quarter_count = '2nd Quater ' + year_count
        elif month_count in quater3:
            quarter_count = '3rd Quater ' + year_count
        elif month_count in quater4:
            quarter_count = '4th Quater ' + year_count
        else:
            quarter_count = 'month name error'
            print("#################### MONTH NAME ERROR  ###########################")
        month_count = dto.strftime('%B') + " " + year_count

        print("date - ", day_count, " contact month: ", month_count, " Year-", year_count, " Week-", week_count,
              " Quater- ", quarter_count)
        print("date - ", type(day_count), " contact month: ", type(month_count), " Year-", type(year_count), " Week-",
              type(week_count), " Quater- ", type(quarter_count))

        for j in fieldFunctions:
            fun = j[: j.find("(")]
            field = j[j.find("(") + 1:j.find(")")]
            if field not in request.env[mod]._fields:
                continue
            sum = i[field]
            print("###################  sum --- ", sum)
            if fun not in return_str:
                return_str[fun] = {}
            if field not in return_str[fun]:
                return_str[fun][field] = {
                    "daily": {},
                    "weekly": {},
                    "monthly": {},
                    "quarterly": {},
                    "yearly": {},
                }

            if fun == "count":
                if year_count not in return_str[fun][field]['yearly'] and (i[field]):
                    return_str[fun][field]['yearly'][year_count] = 1
                elif i[field]:
                    return_str[fun][field]['yearly'][year_count] += 1

                if quarter_count not in return_str[fun][field]['quarterly'] and (i[field]):
                    return_str[fun][field]['quarterly'][quarter_count] = 1
                elif i[field]:
                    return_str[fun][field]['quarterly'][quarter_count] += 1

                if month_count not in return_str[fun][field]['monthly'] and (i[field]):
                    return_str[fun][field]['monthly'][month_count] = 1
                elif i[field]:
                    return_str[fun][field]['monthly'][month_count] += 1

                if ('Week-' + week_count) not in return_str[fun][field]['weekly'] and (i[field]):
                    return_str[fun][field]['weekly']['Week-' + week_count] = 1
                elif i[field]:
                    return_str[fun][field]['weekly']['Week-' + week_count] += 1

                if day_count not in return_str[fun][field]['daily'] and (i[field]):
                    return_str[fun][field]['daily'][day_count] = 1
                elif i[field]:
                    return_str[fun][field]['daily'][day_count] += 1

            if fun == "sum":
                if year_count not in return_str[fun][field]['yearly']:
                    return_str[fun][field]['yearly'][year_count] = sum
                else:
                    return_str[fun][field]['yearly'][year_count] += sum

                if quarter_count not in return_str[fun][field]['quarterly']:
                    return_str[fun][field]['quarterly'][quarter_count] = sum
                else:
                    return_str[fun][field]['quarterly'][quarter_count] += sum

                if month_count not in return_str[fun][field]['monthly']:
                    return_str[fun][field]['monthly'][month_count] = sum
                else:
                    return_str[fun][field]['monthly'][month_count] += sum

                if ('Week-' + week_count) not in return_str[fun][field]['weekly']:
                    return_str[fun][field]['weekly']['Week-' + week_count] = sum
                else:
                    return_str[fun][field]['weekly']['Week-' + week_count] += sum

                if day_count not in return_str[fun][field]['daily']:
                    return_str[fun][field]['daily'][day_count] = sum
                else:
                    return_str[fun][field]['daily'][day_count] += sum
