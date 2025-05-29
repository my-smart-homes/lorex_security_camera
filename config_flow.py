import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_RTSP_PATH, CONF_USERNAME, CONF_PASSWORD

class LorexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            host = user_input[CONF_HOST]
            rtsp = user_input[CONF_RTSP_PATH]
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            return self.async_create_entry(
                title=host,
                data={
                    CONF_HOST: host,
                    CONF_RTSP_PATH: rtsp,
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password
                },
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_RTSP_PATH, default="/live.sdp"): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )