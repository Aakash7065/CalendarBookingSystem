from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from app.mappers.set_availability_request import map_to_set_availability_request
from app.models.models import calendars
from app.services.calendar_service import set_availability, list_upcoming_appointments_for_owner

bp = Blueprint("calendar", __name__)


@bp.route("/set_availability/<owner>", methods=["POST"])
def set_calendar_availability(owner):
    try:
        availability_request = map_to_set_availability_request(request.get_json(force=True))
        response = set_availability(owner, availability_request)
        return jsonify(response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e)}), 400
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/appointments/list_upcoming', methods=['GET'])
def list_upcoming_appointments():
    """Retrieve all upcoming appointments for a calendar owner."""
    owner = request.args.get('owner')
    if not owner:
        return jsonify({"error": "Owner parameter is required"}), 400

    if owner not in calendars:
        return jsonify({"error": "Calendar owner not found"}), 404
    try:
        upcoming_appointments = list_upcoming_appointments_for_owner(owner)
        return jsonify({"upcoming_appointments": upcoming_appointments}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e)}), 400
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
