from data_fetcher import DataFetcher
import requests
import sys
import logging
import logging.config
import traceback
from const import *
import schedule
import time
import os


def main():
    logger_init()
    logging.info("Service start!")

    phone_number = sys.argv[1]
    password = sys.argv[2]
    fetcher = DataFetcher(phone_number, password)
    schedule.every().day.at(JOB_START_TIME).do(run_task, fetcher)
    run_task(fetcher)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_task(data_fetcher: DataFetcher):
    try:
        balance, usage = data_fetcher.fetch()
        update_sensor(BALANCE_SENSOR_NAME, balance, BALANCE_UNIT)
        update_sensor(USAGE_SENSOR_NAME, usage, USAGE_UNIT)
        logging.info("state-refresh task run successfully!")
    except Exception as e:
        logging.error(f"state-refresh task failed, reason is {e}")
        traceback.print_exc()

def update_sensor(sensorName: str, sensorState:float, sensorUnit: str):
        
    supervisor_token = os.getenv("SUPERVISOR_TOKEN")
    headers = {
        "Content-Type": "application-json",
        "Authorization": "Bearer " + supervisor_token 

    }
    request_body = {
        "state":sensorState,
        "attributes": {
            "unit_of_measurement": sensorUnit
        }
    }
    try:        
        response = requests.post(API_URL + sensorName, json = request_body, headers = headers)
        logging.info(f"Homeassistant REST API invoke, POST on {API_URL + sensorName}. response[{response.status_code}]: {response.content}")
    except:
        raise Exception("Sensor update failed, please check the network")


def logger_init():
    logger = logging.getLogger()
    logger.setLevel(sys.argv[3])
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    format = logging.Formatter("%(asctime)s  [%(levelname)-8s] ---- %(message)s","%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(stream=sys.stdout) 
    sh.setFormatter(format)
    logger.addHandler(sh)


if(__name__ == "__main__"):
    main()
