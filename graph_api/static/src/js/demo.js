console.log('demo');
odoo.define('graph_api.demo', function (require) {
    'use strict';
    console.log('demo');
    var options = require('web_editor.snippets.options');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    console.log(options);

    let STATE = {
      models: [],
      fields: [],
      days: 30,
      freq: 'daily',
      tool: 'count'
    }
    var dialog;
    var FormEditorDialog = Dialog.extend({
        init: function (parent, options) {
            this._super(parent, _.extend({
                buttons: [{
                    text: _t('Save'),
                    classes: 'btn-primary',
                    close: true,
                    click: this._onSaveModal.bind(this),
                }, {
                    text: _t('Cancel'),
                    close: true
                }],
            }, options));
        },
        _onSaveModal: function () {
        console.log('saving');
        dialog.opened().then( function (){
            console.log('success')
            var model = $("#model_select option:selected").val()
            console.log(model)
            var days = $("#days_select option:selected").val()
            var frequency = $("#frequency_select option:selected").val()
            var tool = $("#tool option:selected").val()
            var field = $("#fields option:selected").val()

            console.log(field)
            console.log('field')
            if (!field){
                console.log('got')
                return alert('Fields not defined');

            }

            ajax.jsonRpc('/save', 'call', {
               'data' : { 'fre': frequency,
                          'days': days,
                           'model': model,
                           'tool': tool,
                           'field': field},
              })
            //json Rpc Call
            .then(function (data) {
            });
        });
        },
    });
    options.registry.graph_method = options.Class.extend({
    xmlDependencies: ['/graph_api/static/src/xml/param_template.xml'],
        onBuilt : function () {
            console.log('fdddd');

              ajax.jsonRpc('/get/models', 'call').then(function(response){
                response = JSON.parse(response);
                STATE.models = response.models
                console.log(STATE.models);
                console.log(typeof(STATE.models));
                var ParamTemplate = $(QWeb.render("graph_api.ParamTemplate", { models: STATE.models}));
                dialog = new FormEditorDialog(self, {
                    title: 'Graph',
                    size: 'medium',
                    $content: ParamTemplate,
                }).open();
                dialog.opened().then( function () {
                        var model = $("#model_select option:selected").val()
                        document.getElementById("fields").options.length = 0;
                        console.log('here we goo again')

                        ajax.jsonRpc('/get_fields', 'call', {
                           'data' : model,
                          })
                        //json Rpc Call
                        .then(function (data) {
                        console.log(data)
                        data.forEach( function (dd) {
                        console.log(dd)
//                        $('select#fields').find('option').empty()
                        $('select#fields').append(new Option(dd, dd))
                        })
                        });




                        $('select#model_select').on('change', function() {
                        var model = $("#model_select option:selected").val()
                        document.getElementById("fields").options.length = 0;

                        ajax.jsonRpc('/get_fields', 'call', {
                           'data' : model,
                          })
                        //json Rpc Call
                        .then(function (data) {
                        console.log(data)
                        data.forEach( function (dd) {
                        console.log(dd)
//                        $('select#fields').find('option').empty()
                        $('select#fields').append(new Option(dd, dd))
                        })
                        });
                      });
                })

    //            dialog.on('closed', this, cancel);
//                dialog.on('save', this, ev => {
//                    ev.stopPropagation();
//    //                save.call(dialog);
//                });

                    }
                  );
//            var frequency =  $('<select id="frequency" class="mr-2"><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option><option value="quarterly">Quarterly</option><option value="yearly">Yearly</option></select>');
//            var days = $('<select id="days" class="mr-2"><option value="30">Last 30 days</option><option value="60">Last 60 days</option><option value="365">Last 365 days</option><option value="1700">Last 1700 days</option></select>')
//            var $content = $('<form role="form"><h1>hiii</h1>' + 'Frequency :'+frequency +
//                                +'<br></br>'+ 'Days:' + days +'</form>');

        },
    });
    });