from flask_authorize import Authorize
from api import app
from utils.util import my_current_user

authorize = Authorize(current_user=my_current_user)
authorize.init_app(app)
