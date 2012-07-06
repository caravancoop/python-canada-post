VERSION = "0.0.1-2"
"""
Configuration module for the API. This defines whether to use the development
or production credentials/urls (and what the credentials are).
"""

DEBUG = False

DEV = "DEV"
PROD = "PROD"

USERNAME = ""
PASSWORD = ""

CUSTOMER_NUMBER = ""

class Auth(object):
    def __init__(self, username="", password="", dev=PROD):
        self.USERNAME = {
            DEV: "",
            PROD: "",
            }
        self.USERNAME[dev]=username
        self.PASSWORD = {
            DEV: "",
            PROD: "",
        }
        self.PASSWORD[dev] = password

    def set_password(self, password, dev=PROD):
        """
        Set the password.

        @parameter
        `dev`: Whether this is the development or production password. Should
                be canada_post.DEV or canada_post.PROD
        """
        self.PASSWORD[dev] = password

    def set_username(self, username, dev=PROD):
        """
        Set the username.

        @parameter
        `dev`: Whether this is the development or production password. Should
                be canada_post.DEV or canada_post.PROD
        """
        self.USERNAME[dev] = username

AUTH = Auth()
