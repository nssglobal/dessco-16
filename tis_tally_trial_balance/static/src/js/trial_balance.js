odoo.define('tis_tally_trial_balance.trial_balance_report', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
     var utils = require('web.utils');
    var session = require('web.session');
    var QWeb = core.qweb;
    var framework = require('web.framework');
    var rpc = require('web.rpc');
    var _t = core._t;
    var datepicker = require('web.datepicker');
    var time = require('web.time');

    window.click_num = 0;
    var TrialBalance = AbstractAction.extend({
    template: 'TrialTemplateView',
        events: {
            'click #apply_filter': 'apply_filters',
            'click #pdf': 'print_trial_balance_pdf',
            'click #xlsx': 'print_trial_balance_xlsx',
            'click .show-gl': 'show_gl',
            'mousedown div.input-group.date[data-target-input="nearest"]': '_onClickCalendarIcon',
        },
        init: function(parent, action) {
        this._super(parent, action);
                this.currency=action.currency;
                this.report_lines = action.report_lines;
                this.wizard_id = action.context.wizard | null;
            },

        start: function() {
            var self = this;
            self.initial_render = true;
            rpc.query({
                model: 'account.report_trialbalance',
                method: 'create',
                args: [{

                }]
            }).then(function(t_res) {
                self.wizard_id = t_res;
                self.$(".categ").empty();
                try{
                    self._rpc({
                        model: 'account.report_trialbalance',
                        method: 'action_view_report',
                        args: [[self.wizard_id]],
                    }).then(function(datas) {
                            _.each(datas['report_lines'], function(rep_lines) {
                            rep_lines.debit = self.format_currency(datas['currency'],rep_lines.debit);
                            rep_lines.credit = self.format_currency(datas['currency'],rep_lines.credit);
                            rep_lines.balance = self.format_currency(datas['currency'],rep_lines.balance);



                            });
                            if (self.initial_render) {
                                    self.$('.filter_view_tb').html(QWeb.render('TrialTopView', {
                                        filter_data: datas['filters'],
                                    }));
                                    self.$el.find('.journals').select2({
                                        placeholder: 'Select Journals...',
                                    });
                                    self.$el.find('.target_move').select2({
                                        placeholder: 'Target Move...',
                                    });
//                                    self.$el.find('#start_dateee').select2({
//                                        placeholder: 'Date.',
//                                    });
                            }
                            var child=[];

                        self.$('.table_view_tb').html(QWeb.render('TrialTable', {

                                            report_lines : datas['report_lines'],
                                            filter : datas['filters'],
                                            currency : datas['currency'],
                                            credit_total : self.format_currency(datas['currency'],datas['debit_total']),
                                            debit_total : self.format_currency(datas['currency'],datas['debit_total']),
                                        }));

                });
//
                    }
                catch (el) {
                    window.location.href
                    }
//                self.load_data(self.initial_render);
            })
        },

        format_currency: function(currency, amount) {
            if (typeof(amount) != 'number') {
                amount = parseFloat(amount);
            }
            var formatted_value = (parseInt(amount)).toLocaleString(currency[2],{
                minimumFractionDigits: 2
            })
            return formatted_value
        },

                _onClickCalendarIcon: function (ev) {
        var $calendarInputGroup = $(ev.currentTarget);
//
        var calendarOptions = {

            icons : {
                date: 'fa fa-calendar',

            },
            locale : moment.locale(),
            format : time.getLangDateFormat(),
             widgetParent: 'body',
             allowInputToggle: true,
        };
//
        $calendarInputGroup.datetimepicker(calendarOptions);
    },

    apply_filters: function(event) {

            event.preventDefault();
            var self = this;
            self.initial_render = false;




            var filter_data_selected = {};
             var journal_ids = [];
            var journal_text = [];
            var journal_res = document.getElementById("journal_res")
            var journal_list = $(".journals").select2('data')

            for (var i = 0; i < journal_list.length; i++) {
                if(journal_list[i].element[0].selected === true){

                    journal_ids.push(parseInt(journal_list[i].id))
                    if(journal_text.includes(journal_list[i].text) === false){
                        journal_text.push(journal_list[i].text)
                    }
                    journal_res.value = journal_text
                    journal_res.innerHTML=journal_res.value;
                }
            }
            if (journal_list.length == 0){
               journal_res.value = ""
                    journal_res.innerHTML="";

            }
            filter_data_selected.journal_ids = journal_ids

            if (this.$el.find('.datetimepicker-input[name="date_from"]').val()) {
                filter_data_selected.date_from = moment(this.$el.find('.datetimepicker-input[name="date_from"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }

            if (this.$el.find('.datetimepicker-input[name="date_to"]').val()) {
                filter_data_selected.date_to = moment(this.$el.find('.datetimepicker-input[name="date_to"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }
//            if ($("#date_from").val()) {
//                var dateString = $("#date_from").val();
//                filter_data_selected.date_from = dateString;
//            }


//            if ($("#date_to").val()) {
//                var dateString = $("#date_to").val();
//                filter_data_selected.date_to = dateString;
//            }

            if ($(".target_move").length) {
            var post_res = document.getElementById("post_res")
//            filter_data_selected.target_move = $(".target_move")[1].value
//            post_res.value = $(".target_move")[1].value
//                    post_res.innerHTML=post_res.value;
//              if ($(".target_move")[1].value == "") {
//              post_res.innerHTML="posted";
//
//              }
            }
            rpc.query({
                model: 'account.report_trialbalance',
                method: 'write',
                args: [
                    self.wizard_id, filter_data_selected
                ],
            }).then(function(res) {
            self.initial_render = false;
               self.load_data(self.initial_render);
            });
        },


        load_data: function (initial_render = true) {
            var self = this;
                self.$(".categ").empty();
                try{
                    var self = this;
                    self._rpc({
                        model: 'account.report_trialbalance',
                        method: 'action_view_report',
                        args: [[this.wizard_id]],
                    }).then(function(datas) {
                            _.each(datas['report_lines'], function(rep_lines) {
                            rep_lines.debit = self.format_currency(datas['currency'],rep_lines.debit);
                            rep_lines.credit = self.format_currency(datas['currency'],rep_lines.credit);
                            rep_lines.balance = self.format_currency(datas['currency'],rep_lines.balance);



                            });
                            if (initial_render) {
                                    self.$('.filter_view_tb').html(QWeb.render('TrialFilterView', {
                                        filter_data: datas['filters'],
                                    }));
                                    self.$el.find('.journals').select2({
                                        placeholder: 'Select Journals...',
                                    });
                                    self.$el.find('.target_move').select2({
                                        placeholder: 'Target Move...',
                                    });
//                                    self.$el.find('#start_dateee').select2({
//                                        placeholder: 'Date.',
//                                    });
                            }
                            var child=[];

                        self.$('.table_view_tb').html(QWeb.render('TrialTable', {

                                            report_lines : datas['report_lines'],
                                            filter : datas['filters'],
                                            currency : datas['currency'],
                                            credit_total : self.format_currency(datas['currency'],datas['debit_total']),
                                            debit_total : self.format_currency(datas['currency'],datas['debit_total']),
                                        }));

                });

                    }
                catch (el) {
                    window.location.href
                    }
            },



            print_trial_balance_xlsx: function() {
            var self = this;
            self._rpc({
                model: 'account.report_trialbalance',
                method: 'action_view_report',
                args: [
                    [self.wizard_id]
                ],
            }).then(function(data) {
                var action = {
//                    'type': 'ir_actions_dynamic_xlsx_download',
                    'data': {
                         'model': 'account.report_trialbalance',
                         'options': JSON.stringify(data['filters']),
                         'output_format': 'xlsx',
                         'report_data': JSON.stringify(data['report_lines']),
                         'report_name': 'Trial Balance',
                         'dfr_data': JSON.stringify(data),
                    },
                };

//                return self.do_action(action);
                  self.downloadXlsx(action);
            });
        },
        downloadXlsx: function (action){
        framework.blockUI();
            session.get_file({
                url: '/dynamic_trial_xlsx_report',
                data: action.data,
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },
            print_trial_balance_pdf: function(e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'account.report_trialbalance',
                method: 'action_view_report',
                args: [
                    [self.wizard_id]
                ],
            }).then(function(data) {
            console.log("data",data)
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_name': 'tis_tally_trial_balance.trial_balance',
                    'report_file': 'tis_tally_trial_balance.trial_balance',
                    'data': {
                        'report_data': data
                    },
                    'context': {
                        'active_model': 'account.report_trialbalance',
                        'landscape': 1,
                        'trial_dynamic_pdf_report': true
                    },
                    'display_name': 'Trial Balance',
                };
                return self.do_action(action);
            });
        },




        });
    core.action_registry.add("trial_balance_report", TrialBalance);
    return TrialBalance;
});
