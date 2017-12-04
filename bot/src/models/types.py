from src.thrift_models.ttypes import MessageType, InputType, SenderType, MediaType, ButtonType, Medium

class SenderTypeWrapper(SenderType):

    @staticmethod
    def get_name(sender_type):
        return SenderType._VALUES_TO_NAMES[sender_type]

    @staticmethod
    def get_value(name):
        return SenderType._NAMES_TO_VALUES[name]

class MessageTypeWrapper(MessageType):

    @staticmethod
    def get_name(message_type):
        return MessageType._VALUES_TO_NAMES[message_type]

    @staticmethod
    def get_value(name):
        return MessageType._NAMES_TO_VALUES[name]

class InputTypeWrapper(InputType):

    @staticmethod
    def get_name(input_type):
        return InputType._VALUES_TO_NAMES[input_type]

    @staticmethod
    def get_value(name):
        return InputType._NAMES_TO_VALUES[name]

class MediaTypeWrapper(MediaType):

    @staticmethod
    def get_name(media_type):
        return MediaType._VALUES_TO_NAMES[media_type]

    @staticmethod
    def get_value(name):
        return MediaType._NAMES_TO_VALUES[name]

class ButtonTypeWrapper(ButtonType):

    @staticmethod
    def get_name(button_type):
        return ButtonType._VALUES_TO_NAMES[button_type]

    @staticmethod
    def get_value(name):
        return ButtonType._NAMES_TO_VALUES[name]

class MediumWrapper(Medium):

    @staticmethod
    def get_name(medium_type):
        return Medium._VALUES_TO_NAMES[medium_type]

    @staticmethod
    def get_value(name):
        return Medium._NAMES_TO_VALUES[name]
