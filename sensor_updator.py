import requests
from const import *
import logging
import os


class SensorUpdator:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.url = requests.compat.urljoin(self.base_url, API_PATH)

    
    def update(self, sensorName: str, sensorState:float, sensorUnit: str):
        token = os.getenv("SUPERVISOR_TOKEN") if self.base_url == SUPERVISOR_URL else self.token
        headers = {
        "Content-Type": "application-json",
        "Authorization": "Bearer " + token 

        }
        request_body = {
            "state":sensorState,
            "attributes": {
                "unit_of_measurement": sensorUnit
            }
        }

        try:        
            response = requests.post(self.url + sensorName, json = request_body, headers = headers)
            logging.info(f"Homeassistant REST API invoke, POST on {self.url + sensorName}. response[{response.status_code}]: {response.content}")
        except:
            raise Exception("Sensor update failed, please check the network")