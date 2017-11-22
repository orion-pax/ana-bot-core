"""
Message lifecycle goes here, receving to responding
__author__: https://github.com/velutha
"""
import uuid
from src.utils import Util
from src.thrift_models.ttypes import SenderType
from src.models.user import User
from src.models.business import Business
from src.models.ana_node import AnaNode
from src.event_logger import EventLogger
from src.config import flow_config
from src.converters.converter import Converter

class MessageProcessor():

    def __init__(self, message):

        self.meta_data = message["meta"]
        self.message_content = message["data"]

        self.user_id = self.meta_data["sender"]["id"]
        self.business_id = self.meta_data["recipient"]["id"]

        self.flow_data = Business(self.business_id).get_business_data()
        self.flow_id = self.flow_data.get("flow_id", flow_config["default_flow_id"])

        self.sender_type = SenderType._VALUES_TO_NAMES[message["meta"]["senderType"]]
        self.state = self._get_state()

    def respond_to_message(self):

        # convert this into objects
        if self.flow_id == "":
            print("Could not find flow")
            return


        if self.sender_type == "AGENT":
            agent_messages = Converter(self.state).get_agent_messages(self.meta_data, self.message_content)
            # response = self.__respond_with_messages(messages)
            response = Util.send_messages(messages=agent_messages, sending_to="AGENT")
            return response
        else:
            node = self._get_node()
            messages_data = Converter(self.state).get_messages(node, self.meta_data, self.message_content)
            messages = messages_data.get("messages")
            event_data = messages_data.get("event_data")

            agent_messages = [message["message"] for message in messages if message["send_to"] == "AGENT"]
            user_messages = [message["message"] for message in messages if message["send_to"] == "USER"]

            agent_response = Util.send_messages(messages=agent_messages, sending_to="AGENT")
            user_response = Util.send_messages(messages=user_messages, sending_to="USER")
            # agent_response = self.__send_to_agent(agent_messages)
            # user_response = self.__respond_with_messages(user_messages)

            if agent_response or user_response:
                User(self.user_id).set_state(self.session_id, self.state, self.meta_data, self.flow_data)
                EventLogger().log(meta_data=self.meta_data, data=event_data, flow_data=self.flow_data)
                print("User state updated with", self.state)
            return


    def _get_state(self):

        if self.sender_type == "AGENT":
            user_id = self.business_id
        else:
            user_id = self.user_id

        session_id = self.meta_data.get("sessionId", str(uuid.uuid4()))

        state = User(user_id).get_session_data(session_id)

        self.session_id = state["session_id"]
        self.meta_data["sessionId"] = self.session_id

        state["flow_id"] = self.flow_id

        return state

    def _get_node(self):

        if bool(self.state):
            first_node_id = self.flow_id + "." + flow_config["first_node_key"]
            node_id = self.state.get("current_node_id", first_node_id) # give first_node as default
            next_node_data = AnaNode(node_id).get_next_node_data(self.flow_id, self.message_content)

            event_data = next_node_data.get("event_data", {})
            if event_data != {}:
                EventLogger().log(meta_data=self.meta_data, data=event_data, flow_data=self.flow_data)
            next_node_id = next_node_data["node_id"]
            self.state["new_var_data"] = next_node_data["input_data"]
            self.state["current_node_id"] = next_node_id
            node = AnaNode(next_node_id).get_contents(next_node_id)
        else:
            first_node_id = self.flow_id + "." + flow_config["first_node_key"]
            next_node_id = self.flow_id + "." + flow_config["first_node_key"]
            self.state["current_node_id"] = next_node_id
            node = AnaNode(next_node_id).get_contents(next_node_id)

        return node
