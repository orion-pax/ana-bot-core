"""
This module handles combination node of ana studio output
Author: https://github.com/velutha
"""
import json
import re
from furl import furl
from src.logger import logger
from src.config import ana_config
from src.models.types import MessageTypeWrapper as MessageType, InputTypeWrapper as InputType, MediaTypeWrapper as MediaType,\
        ButtonTypeWrapper as ButtonType
from src.models.message import MessageContent, MessageData, Media
from src.models.inputs import Option, Item, TextInput

class CombinationProcessor():

    def __init__(self, state):
        self.state = state
        self.click_inputs = ana_config["click_input_types"]
        self.text_inputs = ana_config["text_input_types"]

    def process_node(self, node_data):

        sections_data = node_data.get("Sections", [])
        buttons_data = node_data.get("Buttons", [])
        sections_response = self.convert_sections(sections_data)
        buttons_response = self.convert_buttons(buttons_data)
        messages = sections_response + buttons_response

        event_log_data = {
            "node_data" : node_data,
            "type_of_event": "view",
            "event_data" : {}
            }

        return {"messages": messages, "events": [event_log_data]}

    def verb_replacer(self, text):
        variable_data = self.state.get("var_data", {})
        matches = re.findall("\[~(.*?)\]", text)
        variable_names = variable_data.keys()
        final_text = text
        for match in matches:
            if match in variable_names:
                key = "[~" + match + "]"
                final_text = text.replace(key, variable_data[match])
        return final_text

    def convert_sections(self, data):
        messages_data = []
        # after the types are handled remove if else clauses
        # convert to objects, preferably using factory pattern
        for section in data:
            section_type = section.get("SectionType", "")
            if section_type == "Text":
                message_type = MessageType.get_value("SIMPLE")
                text = section.get("Text", "")
                final_text = self.verb_replacer(text)
                message_content = MessageContent(text=final_text, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type in ["Image", "Gif"]:
                message_type = MessageType.get_value("SIMPLE")
                media_type = MediaType.get_value("IMAGE")
                url = section.get("Url", "")
                encoded_url = furl(url).url
                preview_url = section.get("PreviewUrl", "")
                text = section.get("Title", "")
                final_text = self.verb_replacer(text)
                media_content = Media(type=media_type, url=encoded_url, previewUrl=preview_url).trim()
                message_content = MessageContent(text=final_text, media=media_content, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type in ["EmbeddedHtml", "Link"]:
                message_type = MessageType.get_value("SIMPLE")
                text = section["Url"]
                message_content = MessageContent(text=text, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type == "Graph":
                pass

            elif section_type == "Video":
                message_type = MessageType.get_value("SIMPLE")
                media_type = MediaType.get_value("VIDEO")
                url = section.get("Url", "")
                encoded_url = furl(url).url
                preview_url = section.get("PreviewUrl", "")
                text = section.get("Title", "")
                final_text = self.verb_replacer(text)
                media_content = Media(type=media_type, url=encoded_url, previewUrl=preview_url).trim()
                message_content = MessageContent(text=final_text, media=media_content, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)

            elif section_type == "Carousel":
                message_type = MessageType.get_value("CAROUSEL")
                section_items = section.get("Items", [])
                item_elements = []
                for section_item in section_items:
                    media_type = MediaType.get_value("IMAGE")
                    image_url = section_item.get("ImageUrl", "")
                    title = section_item.get("Title", "")
                    description = section_item.get("Caption", "")
                    encoded_url = furl(image_url).url
                    media_content = Media(type=media_type, url=encoded_url).trim()
                    buttons = section_item.get("Buttons", [])
                    options = []
                    for button in buttons:
                        if button["Type"] == "OpenUrl":
                            button_title = button.get("Text", "")
                            button_value = json.dumps({"url": button["Url"], "value": button["_id"]})
                            button_type = ButtonType.get_value("URL")
                        else:
                            button_title = button.get("Text", "")
                            button_value = button["_id"]
                            button_type = ButtonType.get_value("ACTION")
                        option_element = Option(title=button_title, value=button_value, type=button_type).trim()
                        options.append(option_element)

                    item_element = Item(title=title, desc=description, media=media_content, options=options).trim()
                    item_elements.append(item_element)
                message_content = MessageContent(items=item_elements, mandatory=1).trim()
                message_data = MessageData(type=message_type, content=message_content).trim()
                messages_data.append(message_data)
            else:
                logger.warning("Unknown section_type found"+str(section_type))

        return messages_data

    def convert_buttons(self, data):

        click_elements = [button for button in data if button["ButtonType"] in self.click_inputs]
        text_elements = [button for button in data if button["ButtonType"] in self.text_inputs]

        messages_data = []


        if click_elements != [] and text_elements == []:
            messages_data = self._process_click_inputs(click_elements, mandatory=1)
        elif click_elements != [] and text_elements != []:
            messages_data = self._process_click_inputs(click_elements, mandatory=0)
        elif click_elements == [] and text_elements != []:
            messages_data = self._process_text_inputs(text_elements)

        return messages_data

    @staticmethod
    def _process_click_inputs(data, mandatory):

        button_heading = None
        elem_message_data = []
        elem_options = []

        message_type = MessageType.get_value("INPUT")
        input_type = InputType.get_value("OPTIONS")

        for button in data:
            button_type = button.get("ButtonType", "")
            if button_type == "OpenUrl":
                button_heading = "Choose an option" # to be compatible with fb quick_replies
                option = {
                    "title": button.get("ButtonName", ""),
                    "value": json.dumps({"url": button["Url"], "value": button["_id"]}),
                    "type": ButtonType.get_value("URL")
                    }
            elif button_type == "NextNode":
                button_heading = "Choose an option" # to be compatible with fb quick_replies
                option = {
                    "title": button.get("ButtonName", button.get("ButtonText", "")),
                    "value": button.get("_id", ""),
                    "type": ButtonType.get_value("QUICK_REPLY")
                    }

            elem_options.append(option)

        if elem_options != []:
            message_content = MessageContent(
                inputType=input_type,
                mandatory=mandatory,
                options=elem_options,
                text=button_heading
                ).trim()
            message_data = MessageData(
                type=message_type,
                content=message_content
                ).trim()
            elem_message_data.append(message_data)

        return elem_message_data

    @staticmethod
    def _process_text_inputs(data):

        elem_message_data = []

        for button in data:
            button_type = button.get("ButtonType")
            message_type = ""
            input_type = ""
            input_attr = None
            content = None

            if button_type == "GetText":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("TEXT")
                input_attr = TextInput(placeHolder=button.get("PlaceholderText", "")).trim()
            elif button_type == "GetNumber":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("NUMERIC")
            elif button_type == "GetPhoneNumber":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("PHONE")
            elif button_type == "GetEmail":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("EMAIL")
            elif button_type == "GetLocation":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("LOCATION")
            elif button_type == "GetAddress":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("ADDRESS")
            elif button_type == "GetDate":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("DATE")
            elif button_type == "GetTime":
                message_type = MessageType.get_value("INPUT")
                input_type = InputType.get_value("TIME")
            elif button_type == "GetItemFromSource":
                pass
            else:
                logger.warning("Undefined Text Input Type" + str(button_type))

            content = MessageContent(
                inputType=input_type,
                textInputAttr=input_attr,
                mandatory=1,
                ).trim()
            message_data = MessageData(
                type=message_type,
                content=content
                ).trim()
            elem_message_data.append(message_data)


        return elem_message_data
