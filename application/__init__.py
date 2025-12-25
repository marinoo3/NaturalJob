from flask import Flask  

from .custom.data import Data
from .custom.nlp import NLP
from .custom.db import UserDB, OfferDB
from .custom.api import NTNE, APEC
from .custom.plot import Plot


class AppContext(Flask):
    data: Data
    user_db: UserDB
    offer_db: OfferDB
    ntne_api: NTNE
    apec_api: APEC
    nlp: NLP
    plot: Plot


def create_app():

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    with app.app_context():
        app.data = Data()
        app.user_db = UserDB()
        app.offer_db = OfferDB()
        app.ntne_api = NTNE()
        app.apec_api = APEC()
        app.nlp = NLP()
        app.plot = Plot()

    # Init pages routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Init backend ajax 
    from .ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint, url_prefix='/ajax')


    return app