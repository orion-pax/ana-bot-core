import json
import urllib.parse
from furl import furl
from src.config import ana_config
from src.thrift_models.ttypes import MessageType, InputType, MediaType
from src.models.message import MessageContent, MessageData, Message, Media
from src.models.inputs import Option, Item, TextInput

class Converter():

    def __init__(self, *args, **kwargs):
        self.messages = []
        # self.section_types = ana_config.section_types
        # self.node_types = ana_config.node_types
        # self.button_types = ana_config.button_types
        pass

    def get_messages_data(self, node_data, message_content):
        if (node_data == {}): 
            return []
        node_type = node_data["NodeType"]
        messages = []
        if node_type == "Combination":
            sections_data = node_data["Sections"]
            buttons_data = node_data["Buttons"]
            sections_response = self.convert_sections(sections_data)
            buttons_response = self.convert_buttons(buttons_data)
            messages = sections_response + buttons_response
        elif node_type == "ApiCall":
            pass
        return messages

    def convert_sections(self,data):
        messages_data = []
        # after the types are handled remove if else clauses
        # convert to objects, preferably using factory pattern
        for section in data:
            section_type = section["SectionType"]
            if section_type == "Text":
                message_type = MessageType._NAMES_TO_VALUES["SIMPLE"]
                text = section["Text"]
                message_content = MessageContent(text=text, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type in ["Image","Gif"]:
                message_type = MessageType._NAMES_TO_VALUES["SIMPLE"]
                media_type = MediaType._NAMES_TO_VALUES["IMAGE"]
                url = section.get("Url","")
                encoded_url = furl(url).url
                preview_url = section.get("PreviewUrl","")
                text = section["Title"]
                media_content = Media(type=media_type, url=encoded_url, previewUrl=preview_url).trim() 
                message_content = MessageContent(text=text, media=media_content, mandatory=0).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type in ["EmbeddedHtml", "Link"]:
                message_type = MessageType._NAMES_TO_VALUES["SIMPLE"]
                text = section["Url"]
                message_content = MessageContent(text=text, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type == "Carousel":
                message_type = MessageType._NAMES_TO_VALUES["CAROUSEL"]
                section_items = section["Items"]
                item_elements = []
                for section_item in section_items:
                    media_type = MediaType._NAMES_TO_VALUES["IMAGE"]
                    image_url = section_item["ImageUrl"]
                    title = section_item["Title"]
                    description = section_item["Caption"]
                    encoded_url = furl(image_url).url
                    media_content = Media(type=media_type, url=encoded_url).trim()
                    buttons = section_item["Buttons"]
                    options = []
                    for button in buttons:
                        button_title = button["Text"]
                        button_value = button["_id"]
                        option_element = Option(title=button_title, value=button_value).trim()
                        options.append(option_element)
                    item_element = Item(title=title, desc=description, media=media_content,options=options).trim() 
                    item_elements.append(item_element)
                message_content = MessageContent(items = item_elements, mandatory=0).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

        return messages_data
        
    def convert_buttons(self,data):
        next_node_elem_message_data = []
        other_elem_message_data = []
        next_node_elements = []
        other_elements = []

        for button in data:
            if button["ButtonType"] == "NextNode":
                next_node_elements.append(button)
            if button["ButtonType"] in ["GetText", "GetNumber", "GetPhoneNumber", "GetEmail"]:
                other_elements.append(button)

        next_node_elem_message_type = MessageType._NAMES_TO_VALUES["INPUT"]
        next_node_elem_input_type = InputType._NAMES_TO_VALUES["OPTIONS"]
        next_node_elem_options = []

        # print(next_node_elements)
        for button in next_node_elements:
            option = {
                    "title": button["ButtonName"],
                    "value": button.get("_id", "")
                    }
            next_node_elem_options.append(option)

        if (next_node_elem_options != []):
            next_node_elem_content = MessageContent(
                    inputType=next_node_elem_input_type,
                    mandatory=0,
                    options=next_node_elem_options
                    ).trim()
            next_node_message_data = MessageData(
                    type=next_node_elem_message_type,
                    content=next_node_elem_content
                    ).trim()
            next_node_elem_message_data.append(next_node_message_data)

        for button in other_elements:
            button_type = button["ButtonType"]
            if button_type == "GetText":
                message_type = MessageType._NAMES_TO_VALUES["INPUT"]
                input_type = InputType._NAMES_TO_VALUES["TEXT"] 
                input_attr = TextInput(placeHolder= button["ButtonText"]).trim()
                content = MessageContent(
                        inputType=input_type,
                        textInputAttr=input_attr,
                        mandatory=1,
                        ).trim()
                message_data = MessageData(
                        type=message_type,
                        content=content
                        ).trim()
                other_elem_message_data.append(message_data)
            elif button_type == "GetNumber":
                message_type = MessageType._NAMES_TO_VALUES["INPUT"]
                input_type = InputType._NAMES_TO_VALUES["NUMERIC"] 
                content = MessageContent(
                        inputType=input_type,
                        mandatory=1,
                        ).trim()
                message_data = MessageData(
                        type=message_type,
                        content=content
                        ).trim()
                other_elem_message_data.append(message_data)
            elif button_type == "GetPhoneNumber":
                message_type = MessageType._NAMES_TO_VALUES["INPUT"]
                input_type = InputType._NAMES_TO_VALUES["PHONE"] 
                content = MessageContent(
                        inputType=input_type,
                        mandatory=1,
                        ).trim()
                message_data = MessageData(
                        type=message_type,
                        content=content
                        ).trim()
                other_elem_message_data.append(message_data)
            elif button_type == "GetEmail":
                message_type = MessageType._NAMES_TO_VALUES["INPUT"]
                input_type = InputType._NAMES_TO_VALUES["EMAIL"] 
                content = MessageContent(
                        inputType=input_type,
                        mandatory=1,
                        ).trim()
                message_data = MessageData(
                        type=message_type,
                        content=content
                        ).trim()
                other_elem_message_data.append(message_data)
            else:
                print(e)
                raise

        messages_data = next_node_elem_message_data + other_elem_message_data
        # for next_node_elements
        # take out nextnode elements and convert them into input.options
        # remaining element as another input element accordingly
        return messages_data

# "ana_section_types" : ["Image", "Text", "Graph", "Gif", "Audio", "Video", "Link", "EmbeddedHtml","Carousel"],
# "ana_node_types" : ["Combination", "ApiCall"],
# "ana_button_types" : ["PostText", "OpenUrl","GetText", "GetAddress", "GetNumber", "GetPhoneNumber","GetEmail","GetImage","GetAudio","GetVideo","GetItemFromSource","NextNode","DeepLink","GetAgent","ApiCall","ShowConfirmation","FetchChatFlow","GetDate","GetTime","GetDateTime","GetLocation"]


# Image, Audio, Video, Gif -> Simple Message with Media Content
# Text, Link, EmbeddedHtml -> Simple Message with Text content ?? what for link and embeddedhtml 
# Carousel -> Carousel Message

# OpenUrl -> Input.Options
# GetAddress -> Input.Address

# GetText -> Input.Text
# GetNumber -> Input.Numeric
# GetPhoneNumber -> Input.Phone
# GetEmail -> Input.Email

# GetImage, GetAudio, GetVideo -> Input.Media
# GetDate -> Input.Date
# GetTime -> Input.Time
# GetDateTime ??
# GetLocation -> Input.Location
# NextNode -> Input.options
# GetItemFromSource,NextNode, GetAgent, DeepLink, GetAgent, ApiCall, ShowConfirmation, FetchChatFlow #handle with different scenario
