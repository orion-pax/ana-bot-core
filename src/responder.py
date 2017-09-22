import requests
import uuid
import json
from pprint import pprint
from src.models.user import User
from src.models.ana_node import AnaNode
from src.config import flow_config
from src.config import application_config
from src.converters.converter import Converter

class MessageProcessor():

    def __init__(self, message, *args, **kwargs):

        self.meta_data = message["meta"]
        self.message_content = message["data"]
        self.user_id = self.meta_data["sender"]["id"]
        self.business_id = self.meta_data["recipient"]["id"]
        self.flow_id = flow_config["flows"][self.business_id].get("flow_id", "")
        self.state = self._get_state()

    def respond_to_message(self):
        node = self._get_node()
        messages = Converter.get_messages(node,self.meta_data, self.message_content)
        print("Final Messages")
        print(messages)
        print("**************")
        # response = self._respond_with_messages(messages)
        # if (response):
            # User(self.user_id, self.session_id).set_state(self.state)
            # print("User state updated")
        # else:
            # print("Could not respond back")

    def _get_state(self):
        user_id = self.meta_data["sender"]["id"]
        self.session_id = self.meta_data.get("sessionId", str(uuid.uuid4()))
        self.meta_data["sessionId"] = self.session_id
        state = User(self.user_id, self.session_id).get_session_data()
        return state

    def _get_node(self):

        if bool(self.state):
            node_id = self.state["last_node_id"]
            print("State exists node_id ", node_id)
            next_node_id = AnaNode(node_id).get_next_node_id(self.flow_id, self.message_content)
            # print("State exists next_node_id is", next_node_id)
            self.state["last_node_id"] = next_node_id
            print(next_node_id)
            # node = AnaNode(next_node_id).get_contents(next_node_id)
        else:
            next_node_id =  self.flow_id + "." + flow_config["first_node_key"]
            self.state["last_node_id"] = next_node_id
            node = AnaNode(next_node_id).get_contents(next_node_id)

        return node

    def _respond_with_messages(self, messages):
        url = application_config["GATEWAY_URL"]
        headers = {"Content-Type" : "application/json"}
        if messages == []:
            pass
        for message in messages:
            pprint(message)
            json_message = json.dumps(message)
            try:
                response = requests.post(url, headers=headers, data=json_message)
                print("APIGateway response")
                pprint(response)
            except Exception as e:
                print(e)
                return 0
        return 1
