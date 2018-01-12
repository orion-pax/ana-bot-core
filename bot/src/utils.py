from functools import reduce
import json
import requests
import uuid
import time
from jsonpath import jsonpath
from src.config import application_config
from src.logger import logger
from src.models.types import SenderTypeWrapper as SenderType
from src.models.user import User
from src.models.business import Business
from src.event_logger import EventLogger
from src import EventLogPool


class Util(object):

    @staticmethod
    def merge_dicts(*args):
        result = {}
        for dictionary in args:
            result.update(dictionary)
        return result

    #@staticmethod
    #def deep_find(dictionary, keys):
    #    if not isinstance(dictionary, dict):
    #        logger.error("Object you passed to deep find is not a dictionary")
    #        return None
    #    if not isinstance(keys, list):
    #        # change it to list if it's one element
    #        keys = [keys]

    #    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

    @staticmethod
    def deep_find(obj, path):
        try:
            logger.debug("obj: " + str(obj))##debug
            logger.debug("path: " + str(path))##debug

            val = jsonpath(obj, path)
            if bool(val) and (type(val) is list) and len(val) == 1:
                val = val[0]
            logger.debug("val: " + str(val) )##debug
            return val
        except Exception as err:
            logger.error(err)
            return None

    @staticmethod
    def prepare_agent_message(message):
        message['meta']['id'] = str(uuid.uuid4())
        message['meta']['timestamp'] = int(time.time())
        return message

    @staticmethod
    def send_messages(messages, sending_to):

        # change whoever is passing sending_to to accept from common
        # sender_type
        endpoints = {"USER": application_config["GATEWAY_URL"], \
                "AGENT": application_config["AGENT_URL"]}
        url = endpoints[sending_to]

        headers = {"Content-Type" : "application/json"}
        if messages == []:
            logger.info("No messages to send to " + str(sending_to))
            return 1
        #This is deliberately synchronous to maintain order of messages being
        #sent
        for message in messages:
            if sending_to == "AGENT":
                message = Util.prepare_agent_message(message)

            logger.info(f"Message sent to {sending_to} {message}")
            json_message = json.dumps(message)
            try:
                response = requests.post(url, headers=headers, data=json_message)
                logger.info(response)
            except Exception as err:
                logger.error(err)
                return 0
        return 1

    @staticmethod
    def update_state(state, meta_data, event):
        """
        This methods updates the state of the user after the message is sent
        For e.g. updating current_node_id
        For now agent is stateless, state corresponds to only user
        """

        sender_type = SenderType.get_name(meta_data["senderType"])

        if sender_type == "AGENT" and event == "HANDOVER":
            user_id = meta_data["recipient"]["id"]
            session_id = meta_data["sessionId"]
            state_saved = User(user_id).set_state(session_id, state, meta_data)
            return state_saved

        if sender_type == "AGENT":
            # no need to update user state
            return

        user_id = meta_data["sender"]["id"]
        session_id = meta_data["sessionId"]
        state_saved = User(user_id).set_state(session_id, state, meta_data)
        return state_saved


    @staticmethod
    def get_current_state(meta_data):
        """
        Gets state of the user in conversation which gives info about where he is in conversation
        Gets info the flow/business to which user belongs to
        For e.g. current_node_id of flow exists in state
        """

        sender_type = SenderType.get_name(meta_data["senderType"])

        if sender_type == "AGENT":
            user_id = meta_data["recipient"]["id"]
            business_id = meta_data["sender"]["id"]
        else:
            user_id = meta_data["sender"]["id"]
            business_id = meta_data["recipient"]["id"]

        state = User(user_id).get_session_data(meta_data=meta_data)
        flow_id = meta_data.get("flowId")

        business_id = flow_id if flow_id else business_id
        flow_data = Business(business_id).get_business_data()
        current_state = Util.merge_dicts(state, flow_data)

        return current_state

    @staticmethod
    def log_events(meta_data, state, events, message_event):
        """
        While the user is responded with messages, there will be some analytics events
        which are recorded for e.g. 'click' event for user clicking the button
        No analytics events are recorded for messages sent by agent as of now
        """

        sender_type = SenderType.get_name(meta_data["senderType"])

        # userId and bizId should be reversed and sent
        #if sender_type=="AGENT" and message_event == "HANDOVER":
        #    for event in events:
        #        data = {
        #            "meta_data": meta_data,
        #            "state_data": state,
        #            "event_data": event
        #            }
        #        EventLogPool.submit(EventLogger().log_event(type_of_event=type_of_event, data=data))
        #    return 1

        if sender_type == "AGENT":
            # no need to log any event as of now
            return

        type_of_event = "analytics"

        for event in events:
            data = {
                "meta_data": meta_data,
                "state_data": state,
                "event_data": event
                }
            EventLogPool.submit(EventLogger().log_event(type_of_event=type_of_event, data=data))

        return 1
