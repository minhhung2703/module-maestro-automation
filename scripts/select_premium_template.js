// select_premium_template.js
// Called by Maestro to trigger visual template search for Premium version
var appVersion = (typeof APP_VERSION !== 'undefined') ? APP_VERSION : 'Premium';
var deviceSerial = (typeof DEVICE_SERIAL !== 'undefined' && DEVICE_SERIAL)
    ? DEVICE_SERIAL
    : ((typeof MAESTRO_DEVICE_UDID !== 'undefined' && MAESTRO_DEVICE_UDID) ? MAESTRO_DEVICE_UDID : '');

if (appVersion === 'Premium') {
    var url = 'http://127.0.0.1:8765/select_restaurant_template?version=Premium';
    if (deviceSerial) {
        url += '&device=' + encodeURIComponent(deviceSerial);
    }
    var response = http.get(url);
    output.status = response.status;
    output.body = response.body;
    if (response.status >= 400) {
        throw new Error('Template search failed (HTTP ' + response.status + '): ' + response.body);
    }
} else {
    output.status = 200;
    output.body = "Skipped for Free version";
}
