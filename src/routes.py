import json
import os
from flask import Response
from flask import request
from src import app
from src.models.user import User
from src.services.refresh_chatflows import RefreshChatFlows as ChatFlowController
from src.services.session_service import SessionController
from src.responder import MessageProcessor

@app.route("/health-check")
def hello_world():
    json_data = json.dumps({"status" : "UP"})
    response = Response(json_data, status=200)
    return response

@app.route("/api/refreshChatFlows")
def populate_ana_flows():

    data = ChatFlowController().populate_flows()
    json_data = json.dumps(data)

    response = Response(json_data, status=200, mimetype="application/json")
    return response

@app.route("/api/clearSessions")
def clear_sessions():

    user_id = request.args.get("user_id")

    if (user_id is None):
        message = json.dumps({"message": "user_id missing"}) 
        response = Response(message, status=400, mimetype="application/json")
    else:
        session_response = SessionController().clear_sessions(user_id) 
        json_response = json.dumps(session_response)
        response = Response(json_response, status=200, mimetype="application/json")

    return response

@app.route("/api/userData", methods = ["GET"])
def get_user_data():    

    # change it to a better place
    user_id = request.args.get("user_id")
    session_id = request.args.get("session_id")
    user_key = ""
    if (user_id and session_id):
        print(user_id)
        print(session_id)
        data = User(user_id, session_id).get_session_data()
        print(data)
        json_data = json.dumps(data)
        response = Response(json_data, status=200, mimetype="application/json")
        print(response)
        return response
    else:
        response = Response({"message": "missing params"}, status=400, mimetype="application/json")
        return response

@app.route("/api/message", methods=["POST"])
def message_handler():
    message = request.get_json()
    print("Message Received")
    print(message)
    print("****************")
    response = MessageProcessor(message).start()
    return "OK"
