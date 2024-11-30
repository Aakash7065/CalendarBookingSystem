from flask import Flask
from app.routes import calendar, appointments

def create_app():
    app = Flask(__name__)
    app.register_blueprint(calendar.bp, url_prefix="/api/calendar")
    app.register_blueprint(appointments.bp, url_prefix="/api/appointments")
    return app