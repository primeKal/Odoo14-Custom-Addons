from datetime import datetime
from datetime import timedelta

from odoo import fields, models, api, registry, sql_db
from odoo.exceptions import UserError


class Meeting(models.Model):
    _name = "meeting"
    _description = "Model for scheduling meetings and attendees "
    _order = "create_date desc"

    name = fields.Char(string="Name")
    descri = fields.Char(string="Description", required=True)
    start = fields.Datetime(string="Starting Time", required=True)
    delay = fields.Char("Delay", required=True)
    delay_type = fields.Selection([
        ("h", "Hours"),
        ("m", "Minutes")], "Delay Type", required=True)
    # owner = fields.Many2one("res.users", string="Creator")
    attendees = fields.Many2many("res.users", string="Attendees")
    status = fields.Selection([
        ("p", "Passed"),
        ("s", "Scheduled"),
        ('h', "Happening")], "Status", compute='_setStatus', store=True)

    end = fields.Datetime(compute='_endTime', store=True)

    @api.depends('start', 'delay')
    def _endTime(self):
        for record in self:
            if record.create_uid:
                meeting_ibj = self.env['meeting']
                start = record.start
                # start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                print(start)
                if (record.delay_type == 'm'):
                    time_change = timedelta(minutes=int(record.delay))
                    end = start + time_change
                    print(end)
                    self.end = end
                else:
                    time_change = timedelta(hours=int(record.delay))
                    end = start + time_change
                    print(end)
                    self.end = end

    # get ready to over ride te create method and
    # just change te status according to the time

    @api.depends('start')
    def _setStatus(self):
        for record in self:
            if record.create_uid:
                check = self.check_date()
                if check == 1:
                    self.status = 's'
                elif check == 2:
                    self.status = 'h'
                elif check == 0:
                    self.status = 'p'

    # @api.model
    # def create(self, vals):
    #     self.check_date(vals)
    #     if()
    #     rec = super(Meeting, self).create(vals)
    #     return rec

    @api.depends('start')
    def check_date(self):
        st = self.start
        end = self.end
        now = datetime.now()
        if st < now < end:
            return 2
        elif st > now:
            return 1
        elif now > end:
            return 0

    # method to be called with automation

    def check_all_meetings(self):
        meeting_obj = self.env['meeting'].search([])
        for meeting in meeting_obj:
            now = datetime.now()
            st = meeting.start
            end = meeting.end
            if st < now < end:
                meeting.status = 'h'
            elif st > now:
                meeting.status = 's'
            elif now > end:
                meeting.status = 'p'

    @api.constrains('start', 'end')
    def _check_happening_meeting(self):
        meeting_obj = self.env['meeting'].search([])
        current_st = self.start
        current_end = self.end
        for meeting in meeting_obj:
            st = meeting.start
            end = meeting.end
            if st < current_st < end:
                raise UserError("There is another meeting at the specified time")
            elif st < current_end < end:
                raise UserError("There is another meeting at the specified time")
            elif current_st < st and current_end > st:
                raise UserError("There is another meeting at the specified time")
            elif current_end > end and current_st < end:
                raise UserError("There is another meeting at the specified time")
