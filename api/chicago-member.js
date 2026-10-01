// Chicago-Midwest Chapter membership application relay — see lib/form-relay.js.
const { makeFormRelay } = require('../lib/form-relay');

module.exports = makeFormRelay({
  formIdEnv: 'CHICAGO_GOOGLE_FORM_ID',
  pagePath: '/chicago-member-form.html',
  emailField: 'entry.1298910614',
  allowedFields: [
    'entry.1290197750', 'entry.558134048', 'entry.426090610', 'entry.1309111243',
    'entry.1364430667', 'entry.1760204923', 'entry.179688324', 'entry.249254206',
    'entry.367519610', 'entry.1281953207', 'entry.1529441216', 'entry.1120090583',
    'entry.1298910614', 'entry.2145626856', 'entry.185058050', 'entry.380321870',
    'entry.737816238', 'entry.748150148', 'entry.507203777', 'entry.1456114443',
    'entry.2048923769', 'entry.733813499', 'entry.778996256',
    'entry.1944699648_year', 'entry.1944699648_month', 'entry.1944699648_day',
    'entry.2062337550', 'entry.1477479964', 'entry.1800543706', 'entry.353631577',
    'entry.684907404',
  ],
  requiredFields: [
    'entry.1290197750', 'entry.558134048', 'entry.1309111243', 'entry.1760204923',
    'entry.249254206', 'entry.367519610', 'entry.1281953207', 'entry.1529441216',
    'entry.1120090583', 'entry.1298910614', 'entry.737816238', 'entry.748150148',
    'entry.507203777', 'entry.1456114443', 'entry.2048923769', 'entry.733813499',
    'entry.778996256', 'entry.1944699648_year', 'entry.1944699648_month',
    'entry.1944699648_day', 'entry.2062337550', 'entry.1477479964',
    'entry.1800543706', 'entry.353631577', 'entry.684907404',
  ],
});
