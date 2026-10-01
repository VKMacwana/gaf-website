// Volunteer application relay — see lib/form-relay.js.
const { makeFormRelay } = require('../lib/form-relay');

module.exports = makeFormRelay({
  formIdEnv: 'GOOGLE_FORM_ID',
  pagePath: '/volunteer.html',
  emailField: 'entry.210922796',
  allowedFields: [
    'entry.104267672', 'entry.1878931564', 'entry.1758107480', 'entry.210922796',
    'entry.180463190', 'entry.351343652', 'entry.1902576848', 'entry.1217335692',
    'entry.536999269', 'entry.1105281222', 'entry.2018990515', 'entry.151151085',
    'entry.624268176', 'entry.558655557', 'entry.558655557.other_option_response',
    'entry.790494099', 'entry.790494099.other_option_response', 'entry.450724413',
    'entry.1344406168', 'entry.1928189581', 'entry.1455580948', 'entry.1569449606',
    'entry.321547063_month', 'entry.321547063_day', 'entry.321547063_year',
  ],
  requiredFields: [
    'entry.1878931564', 'entry.1758107480', 'entry.210922796', 'entry.180463190',
    'entry.351343652', 'entry.1902576848', 'entry.1217335692', 'entry.536999269',
    'entry.1105281222', 'entry.2018990515', 'entry.624268176', 'entry.558655557',
    'entry.790494099', 'entry.450724413', 'entry.1344406168', 'entry.1928189581',
    'entry.1455580948', 'entry.1569449606',
  ],
});
