import html
import json
from local.Logging import Logger
logger = Logger(__file__)

class Sanitize:
    """
    Goal is to prevent malicious input
    """
    def __init__(self):
        pass

    @staticmethod
    def __html_escape(value:str):
        return html.escape(value)

    @staticmethod
    def is_safe_for_python(value:str):
        if callable(value):
            # Python can run this (Datatype == Object or method or class)
            return False

        try:
            json.loads(value)
        except Exception as e:
            # Failed, so it isn't json
            return True
        else:
            # Success so its dangerous
            return False

    @staticmethod
    def is_safe_for_javascript(value:str):
        """Checks if a string contains common JavaScript patterns."""
        # Check for JavaScript keywords and syntax
        keywords = ["function", "var", "let", "const", "if", "else", "for", "while", "return", "new", "this"]
        for keyword in keywords:
            if keyword in value:
                return False

        # Check for JavaScript function calls
        if "(" in value and ")" in value:
            return False

        # Check for JavaScript object notation (JSON)
        if "{" in value and "}" in value:
            return False

        return True

    def validate_string(self, value:str):
        val = self.__html_escape(value)
        if self.is_safe_for_javascript(val) and self.is_safe_for_python(val):
            return val
        else:
            return False
