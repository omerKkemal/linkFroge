from flask import Flask

from webApp.api import api
from webApp.view.login_view import login_view
from webApp.view.auth_view import auth_view
from webApp.utility.setting import Setting
from webApp.database.manage_db import create_all_tables

create_all_tables()  # Ensure all tables are created before the app starts
app = Flask(__name__)

config = Setting()
config.setting_var()
app.secret_key = config.ID(10)

app.register_blueprint(login_view)
app.register_blueprint(auth_view)
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE, host=config.HOST, port=config.PORT)