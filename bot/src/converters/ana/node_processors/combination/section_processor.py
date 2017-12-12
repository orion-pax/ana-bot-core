"""
This module handles sections inside combination node of ana studio output
Author: https://github.com/velutha
"""
import json
import re
from furl import furl
from src.logger import logger
from src.models.types import MessageTypeWrapper as MessageType, MediaTypeWrapper as MediaType, ButtonTypeWrapper as ButtonType
from src.models.message import MessageContentWrapper as MessageContent, MessageDataWrapper as MessageData, MediaWrapper as Media
from src.models.inputs import OptionWrapper as Option, ItemWrapper as Item

class SectionProcessor():

    def __init__(self, state):
        self.state = state

    def process(self, sections):
        messages_data = []

        section_processor_map = {
            "Text": self.__text_processor,
            "EmbeddedHtml": self.__text_processor,
            "Link": self.__text_processor,
            "Image": self.__media_processor,
            "Gif": self.__media_processor,
            "Video": self.__media_processor,
            "Carousel": self.__carousel_processor
            }

        for section in sections:
            section_type = section.get("SectionType", "")
            processor = section_processor_map[section_type]
            if processor is None:
                logger.error(f"Unknown section type found {section_type}")
            else:
                message_data = processor(section)
                messages_data.append(message_data)

        return messages_data

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

    def __text_processor(self, data):

        message_type = MessageType.get_value("SIMPLE")
        section_type = data.get("SectionType")
        if section_type == "Text":
            text = data.get("Text", "")
            text = self.verb_replacer(text)
        elif section_type in ["EmbeddedHtml", "Link"]:
            text = data.get("Url", "")
        message_content = MessageContent(text=text, mandatory=1).trim()
        message_data = MessageData(type=message_type, content=message_content).trim()

        return message_data


    def __media_processor(self, data):

        message_type = MessageType.get_value("SIMPLE")
        section_type = data.get("SectionType")
        if section_type in ["Image", "Gif"]:
            media_type = MediaType.get_value("IMAGE")
        elif section_type == "Video":
            media_type = MediaType.get_value("VIDEO")

        url = data.get("Url", "")
        url = furl(url).url
        preview_url = data.get("PreviewUrl", "")
        preview_url = furl(preview_url).url
        text = data.get("Title", "")
        text = self.verb_replacer(text)
        media_content = Media(type=media_type, url=url, previewUrl=preview_url).trim()
        message_content = MessageContent(text=text, media=media_content, mandatory=1).trim()
        message_data = MessageData(type=message_type, content=message_content).trim()

        return message_data


    @classmethod
    def __carousel_processor(cls, data):

        message_type = MessageType.get_value("CAROUSEL")
        section_items = data.get("Items", [])
        item_elements = []
        for section_item in section_items:
            media_type = MediaType.get_value("IMAGE")
            image_url = section_item.get("ImageUrl", "")
            image_url = furl(image_url).url
            title = section_item.get("Title", "")
            description = section_item.get("Caption", "")
            media_content = Media(type=media_type, url=image_url).trim()
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

        return message_data
