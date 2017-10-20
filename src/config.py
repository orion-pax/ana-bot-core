import os 
import uuid

application_config = {
        "CHATCORE_QUEUE_URL" : os.environ.get("CHATCORE_QUEUE_URL"),
        "GATEWAY_URL": os.environ.get("GATEWAY_URL"),
        "AWS_ACCESS_KEY_ID" : os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_ACCESS_SECRET_KEY" : os.environ.get("AWS_ACCESS_SECRET_KEY"),
        "AWS_REGION" : os.environ.get("AWS_REGION")
        }

default_business_id = os.environ.get("DEFAULT_BUSINESS_ID")
default_flow_api = os.environ.get("DEFAULT_FLOW_API")
default_flow_id = os.environ.get("DEFAULT_FLOW_ID")
print(default_flow_id)
print(default_flow_api)
# each object represents config for one business
flow_config = {
        "first_node_key": "GET_STARTED_NODE",
        "default_flow_api": os.environ.get("DEFAULT_FLOW_API"),
        "default_flow_id": default_flow_id,
        "default_business_id": default_business_id,
        "archived_node_ids": ["INIT_CHAT_NODE", "SEND_CHAT_HISTORY_TO_SERVER", "GET_CHAT_TEXT_NODE", "SEND_CHAT_TEXT_NODE","CONTINUE_CHAT_NODE"],  
        "flows": {
            default_business_id: {
                "flow_id": default_flow_id,
                "api": default_flow_api
                },
            "demo-automobiles": {
                "flow_id": "demo-automobiles",
                "api": "http://ria.nowfloatsdev.com/websitesamples/api/Conversation/chat?projectId=59ea2acab02a292edc83d5d2"
            },
            "demo-ecommerce": {
                "flow_id": "demo-ecommerce",
                "api": "http://ria.nowfloatsdev.com/websitesamples/api/Conversation/chat?projectId=59ea3dc7b02a292edc83d69d"
            },
            "demo-real-estate": {
                "flow_id": "demo-real-estate",
                "api": "http://ria.nowfloatsdev.com/websitesamples/api/Conversation/chat?projectId=59ea3d46b02a292edc83d670"
            }
            }
        }

ana_config = {
        "click_input_types" : ["NextNode", "OpenUrl", "GetFile", "GetAudio", "PostText", "GetImage", "GetAgent"],
        "text_input_types" : ["GetText", "GetEmail", "GetNumber", "GetPhoneNumber", "GetItemFromSource"],
        "ana_section_types" : ["Image", "Text", "Graph", "Gif", "Audio", "Video", "Link", "EmbeddedHtml","Carousel"],
        "ana_node_types" : ["Combination", "ApiCall"],
        "ana_button_types" : ["PostText", "OpenUrl","GetText", "GetAddress", "GetNumber", "GetPhoneNumber","GetEmail","GetImage","GetAudio","GetVideo","GetItemFromSource","NextNode","DeepLink","GetAgent","ApiCall","ShowConfirmation","FetchChatFlow","GetDate","GetTime","GetDateTime","GetLocation"]
        }
