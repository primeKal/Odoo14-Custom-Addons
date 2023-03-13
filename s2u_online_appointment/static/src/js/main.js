odoo.define('s2u_online_appoinment.main', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.OnlineAppointment = publicWidget.Widget.extend({
        selector: '#s2u_online_appointment',
        init: function () {
            this._super.apply(this, arguments);

            this.days_with_free_slots = {};
            this.focus_year = 0;
            this.focus_month = 0;
        },
        // events: {
        //    'click .timeslot_option' :'select_timeslot',
        // },
        start: function () {
            var self = this;
            $('#timezone-input').val(Intl.DateTimeFormat().resolvedOptions().timeZone);
            var dateToday = new Date();
            $('.datepicker').datepicker({
                dateFormat: 'dd/mm/yy',
                startDate: '-3d',
                minDate: dateToday,
            });
            $("#appointment_slot").on('change', function() {
                self.days_with_free_slots = {};
                self._update_timeslot();
            });

            $("#appointment_date").on('change', function() {
                self._update_timeslot();
            });

            // self._update_timeslot();
        },
        // select_timeslot: function (ev){
        //     var currentTarget = $(ev.currentTarget)
        //     currentTarget.siblings().removeClass('bg-primary');
        //     currentTarget.toggleClass('bg-primary');
        //     $('#appointment_time').val(currentTarget.data()['slot_datetime']);
        // },
        _format_date: function (date) {
            var self = this;

            var d = new Date(date),
                month = '' + (d.getMonth() + 1),
                day = '' + d.getDate(),
                year = d.getFullYear();

            if (month.length < 2)
                month = '0' + month;
            if (day.length < 2)
                day = '0' + day;

            return [year, month, day].join('-');
        },
        _update_timeslot: function () {
            var self = this;
            var appointment_slot = $("#appointment_slot").val();
            var appointment_date = $("#appointment_date").val();
            var time_slot_parent = $('#group_slot_id');
            let appointment_time = time_slot_parent.find('#appointment_time');
            if(!appointment_date.length || !appointment_slot){
                // appointment_time.empty();
                return false;
            }
            $.blockUI()
            this._rpc({
                route: '/online-appointment/timeslots',
                params: {
                    'appointment_date': $("#appointment_date").val(),
                    'appointment_slot': $("#appointment_slot").val(),
                    'appointment_group_id':$("input[name='calendar_group']").val(),
                    'tz': Intl.DateTimeFormat().resolvedOptions().timeZone
                },
            }).then(function(result) {

                appointment_time.empty();
                appointment_time.append(`<option value="">${_t('Select a slot')}</option>`)

                $.each(result, function (key, value){
                    console.log(key);
                    console.log(value);
                    appointment_time.append(`<option value="${value}">${key}</option>`);
                });
                if(Object.keys(result).length){
                    time_slot_parent.removeClass('d-none');
                }else{
                    if(time_slot_parent.hasClass('d-none')){
                        time_slot_parent.addClass('d-none');
                    }
                }
            }).finally(function (){
                $.unblockUI();
            });
        },

        _update_days_with_free_slots: function (year, month) {
            var self = this;

            this._rpc({
                route: '/online-appointment/month-bookable',
                params: {
                    'appointment_option': $("#appointment_option_id").val(),
                    'appointment_with': $("#appointee_id").val(),
                    'appointment_year': year,
                    'appointment_month': month,
                    'form_criteria': $("#form_criteria").val(),
                },
            }).then(function(result) {
                self.focus_year = result.focus_year;
                self.focus_month = result.focus_month;
                self.days_with_free_slots[self._get_yearmonth_key.bind(self)()] = result.days_with_free_slots;
                $(".datepicker" ).datepicker("refresh");
            });
        },

        _get_yearmonth_key: function() {
            var key = this.focus_year.toString() + ',' + this.focus_month.toString();
            return key
        },

    }),

    publicWidget.registry.OnlineAppointmentPortal = publicWidget.Widget.extend({
        selector: '#online_appointment_interaction',
        start: function () {
            var self = this;
            var button_cancel = $('#cancel_appointment_button');
            var button_confirm = $('#confirm_appointment_button');

            button_cancel.click(function() {
                var dialog = $('#cancel_appointment_dialog').modal('show');
            });

            button_confirm.click(function() {
                var dialog = $('#confirm_appointment_dialog').modal('show');
            });
        }
    })
});
