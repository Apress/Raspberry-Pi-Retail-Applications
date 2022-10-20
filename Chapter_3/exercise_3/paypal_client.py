import os
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment

import sys

class PayPalClient:
    def __init__(self):
        self.client_id =  os.environ["PAYPAL_CLIENT_ID"] if 'PAYPAL_CLIENT_ID' in os.environ else "" #AfNBWjbEXBtGehBCuNtyu4BV8-sQsSb3HmjMRJWJz63DyJzGHNIGiZpWqpg8aDZwIHeP1f1372EQ5lLG
        self.client_secret = os.environ["PAYPAL_CLIENT_SECRET"] if 'PAYPAL_CLIENT_SECRET' in os.environ else "" #EPnxOP4phNkQnyQ_Bg3v0Y4Esv0U-aRQMPVIXfELyHLTjVCD9p7zNGcp-LLC4OJHTYOfVlegHvwHRmq9

        """Setting up and Returns PayPal SDK environment with PayPal Access credentials.
           For demo purpose, we are using SandboxEnvironment. In production this will be
           LiveEnvironment."""
        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)

        """ Returns PayPal HTTP client instance with environment which has access
            credentials context. This can be used invoke PayPal API's provided the
            credentials have the access to do so. """
        self.client = PayPalHttpClient(self.environment)

    def object_to_json(self, json_data):
        """
        Function to print all json data in an organized readable manner
        """
        result = {}
        if sys.version_info[0] < 3:
            itr = iter(json_data.__dict__.items())
        else:
            itr = list(json_data.__dict__.items())
        for key,value in itr:
            # Skip internal attributes.
            if key.startswith("__") or key.startswith("_"):
                continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
                        self.object_to_json(value) if not self.is_primittive(value) else\
                         value
        return result;
    def array_to_json_array(self, json_array):
        result =[]
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if  not self.is_primittive(item) \
                              else self.array_to_json_array(item) if isinstance(item, list) else item)
        return result;

    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, str) or isinstance(data, int)
