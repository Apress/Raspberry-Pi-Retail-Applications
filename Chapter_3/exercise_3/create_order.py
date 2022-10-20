from paypal_client import PayPalClient
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalhttp.serializers.json_serializer import Json
import json

class CreateOrder(PayPalClient):

    """Setting up the JSON request body for creating the Order. The Intent in the
        request body should be set as "CAPTURE" for capture intent flow."""

    @staticmethod
    def build_request_body(price, item, hostname):
        """Method to create body with CAPTURE intent"""
        return \
            {
                "intent": "CAPTURE",
                "application_context": {
                    "return_url": "http://" + hostname + "/success",
                    "cancel_url": "http://" + hostname + "/cancel",
                    "brand_name": "EXAMPLE INC",
                    "landing_page": "BILLING",
                    "shipping_preference": "SET_PROVIDED_ADDRESS",
                    "user_action": "CONTINUE"
                },
                "purchase_units": [
                    {
                        "reference_id": "PUHF",
                        "description": "Sporting Goods",

                        "custom_id": "Vedi Vending",
                        "soft_descriptor": "Vending machines",
                        "amount": {
                            "currency_code": "USD",
                            "value": price+price*0.1,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value": price
                                },
                                "shipping": {
                                    "currency_code": "USD",
                                    "value": "0.00"
                                },
                                "handling": {
                                    "currency_code": "USD",
                                    "value": "0.00"
                                },
                                "tax_total": {
                                    "currency_code": "USD",
                                    "value": price*0.1
                                },
                                "shipping_discount": {
                                    "currency_code": "USD",
                                    "value": "0"
                                }
                            }
                        },
                        "items": [
                            {
                                "name": item,
                                "description": "Vending item",
                                "sku": "sku01",
                                "unit_amount": {
                                    "currency_code": "USD",
                                    "value": price
                                },
                                "tax": {
                                    "currency_code": "USD",
                                    "value": price*0.1
                                },
                                "quantity": "1",
                                "category": "PHYSICAL_GOODS"
                            },
                        ],
                        "shipping": {
                            "method": "United States Postal Service",
                            "name": {
                                "full_name":"John Doe"
                            },
                            "address": {
                                "address_line_1": "123 Townsend St",
                                "address_line_2": "Floor 6",
                                "admin_area_2": "San Francisco",
                                "admin_area_1": "CA",
                                "postal_code": "94107",
                                "country_code": "US"
                            }
                        }
                    }
                ]
            }

    """ This is the sample function which can be sued to create an order. It uses the
        JSON body returned by buildRequestBody() to create an new Order."""

    def create_order(self, price, item, hostname, debug=False):
        request = OrdersCreateRequest()
        request.headers['prefer'] = 'return=representation'
        request.request_body(self.build_request_body(price, item, hostname))
        response = self.client.execute(request)
        if debug:
            print('Status Code: ', response.status_code)
            print('Status: ', response.result.status)
            print('Order ID: ', response.result.id)
            print('Intent: ', response.result.intent)
            print('Links:')
            for link in response.result.links:
                print(('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method)))
            print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                               response.result.purchase_units[0].amount.value))
            json_data = self.object_to_json(response.result)
            print("json_data: ", json.dumps(json_data,indent=4))
        return response

"""This is the driver function which invokes the createOrder function to create
   an sample order."""
if __name__ == "__main__":
    CreateOrder().create_order(debug=True)
