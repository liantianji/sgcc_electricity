from data_fetcher import DataFetcher
from sensor_updator import SensorUpdator
import sys
import logging
import logging.config
import traceback
from const import *
import schedule
import time
import re

def main():
    args = argvs_parsor()
    logger_init(args["log_level"])
    logging.info("Service start!")

    fetcher = DataFetcher(args["phone_number"], args["password"])
    updator = SensorUpdator(args["hass_url"], args["hass_token"])
    schedule.every().day.at(JOB_START_TIME).do(run_task, fetcher, updator)
    run_task(fetcher, updator)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_task(data_fetcher: DataFetcher, sensor_updator: SensorUpdator):
    try:
        balance, usage = data_fetcher.fetch()
        sensor_updator.update(BALANCE_SENSOR_NAME, balance, BALANCE_UNIT,)
        sensor_updator.update(USAGE_SENSOR_NAME, usage, USAGE_UNIT)
        logging.info("state-refresh task run successfully!")
    except Exception as e:
        logging.error(f"state-refresh task failed, reason is {e}")
        traceback.print_exc()


def argvs_parsor():
    args = {
    "phone_number": "",
    "password":"",
    "log_level":"INFO",
    "hass_url":"",
    "hass_token":""
    }
    pattern = r"--(.*)=(.*)"
    
    for arg in sys.argv[1:]:
        match_result = re.match(pattern,arg)
        if(None != match_result):
            vars = match_result.groups()
            key = vars[0].lower()
            if(len(vars) == 2 and None != args[key]):
                args[key] = vars[1]

    for value in args.values():
        if(len(value) == 0):
            raise Exception("error occured when parsing args. Have you set all required environment variable?")
    return args

def logger_init(level: str):
    logger = logging.getLogger()
    logger.setLevel(level)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    format = logging.Formatter("%(asctime)s  [%(levelname)-8s] ---- %(message)s","%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(stream=sys.stdout) 
    sh.setFormatter(format)
    logger.addHandler(sh)


if(__name__ == "__main__"):
    main()
