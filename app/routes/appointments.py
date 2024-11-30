from flask import Blueprint, request, jsonify

from app.mappers.book_time_slot_request import map_to_book_time_slot_request
from app.mappers.search_availability_request import map_to_search_availability_request
from app.services.booking_service import search_time_slots, book_time_slot

bp = Blueprint("appointments", __name__)

@bp.route("/search_slots", methods=["GET"])
def search_available_slots():
    try:
        payload = request.get_json(force=True) or {}
        search_availability_request = map_to_search_availability_request(payload)
        response = search_time_slots(search_availability_request)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in search_available_slots: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@bp.route("/book_slot", methods=["POST"])
def book_time_slot_api():
    """
    Book a time slot for a given calendar owner and invitee.
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Request payload is empty"}), 400
        book_time_slot_request = map_to_book_time_slot_request(data)
        result = book_time_slot(book_time_slot_request)
        return jsonify(result), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": f"An error occurred time slot booking: {str(e)}"}), 500