odoo.define('absence_day.absence_day', function(require) {
    'use strict';

    var core = require('web.core');
    var time = require('web.time');
    var WorkEntryControllerMixin = require('hr_payroll.WorkEntryControllerMixin');
//    console.log(WorkEntryControllerMixin)
    var _t = core._t;
    var QWeb = core.qweb;

    function _generateWorkEntries(){
        console.log('HR entry will not be created.');
    }

    WorkEntryControllerMixin._generateWorkEntries = _generateWorkEntries

});
