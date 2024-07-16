import sys
import os

# Add the grandparent directory to the Python path
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, path_to_add)
print('Added path:', path_to_add)

from common.utils import *
import math, time
from datetime import datetime
import pandas as pd
import asyncio

from apscheduler.schedulers.background import BackgroundScheduler

import requests
from solana.rpc.api import Client as SolanaClient
from bitquery import Bitquery

from common.utils import *
from service.App import *
from service.analyzer import *

import logging
log = logging.getLogger('collector_depth')

#
# Request order book every 5 seconds and store in the local in-memory database
# The collected results are stored in files - one per day
#


async def main_collector_depth_task():
    """It will be executed for each depth collection, for example, every 5 seconds."""
    log.info(f"===> Start depth collection task.")
    start_time = datetime.utcnow()

    #
    # Get parameters for data collection
    #
    symbols = App.config["collector"]["depth"]["symbols"]
    limit = App.config["collector"]["depth"]["limit"]
    freq = App.config["collector"]["depth"]["freq"]

    #
    # Submit tasks for requesting data and process results
    #
    #coros = [request_depth(sym, freq, limit) for sym in symbols]
    tasks = [asyncio.create_task(request_depth(sym, freq, limit)) for sym in symbols]

    results = []
    timeout = 3  # seconds

    # Process responses in the order of arrival
    for fut in asyncio.as_completed(tasks, timeout=timeout):
        try:
            res = await fut
            results.append(res)
            try:
                # Ensure App.analyzer is not None
                if App.analyzer is not None:
                    # Add to the database
                    added_count = App.analyzer.store_depth([res], freq)
                else:
                    log.error("App.analyzer is not initialized.")
            except Exception as e:
                log.error(f"Error storing order book result in the database: {str(e)}")
        except TimeoutError as te:
            log.warning(f"Timeout {timeout} seconds when requesting order book data.")
        except Exception as e:
            log.warning(f"Exception when requesting order book data: {str(e)}")

    """
    # Process the results after all responses are received
    # Wait for their result
    #results = await asyncio.gather(*coros, return_exceptions=False)
    #await asyncio.wait(tasks, timeout=3)
    for t in tasks:
        try:
            res = t.result()
            results.append(res)
        except Exception as e:
            log.warning(f"Exception returned from a order book request: {str(e)}")
        else:
            pass
    """

    #
    # Store the results
    #
    #added_count = App.analyzer.store_depth(results, freq)

    end_time = datetime.utcnow()
    duration = (end_time-start_time).total_seconds()
    log.info(f"<=== End depth collection task. {len(results)} responses stored. {duration:.2f} seconds processing time.")


async def request_depth(symbol, freq, limit):
    """Request order book data from Bitquery for one symbol."""
    requestTime = now_timestamp()

    depth = {}
    if App.client is None:
        log.error("App.client is not initialized.")
        return depth

    try:
        query = Bitquery.get_order_book_query(symbol, limit)
        response = requests.post(Bitquery.API_URL, json=query)
        depth = response.json()
    except Exception as e:
        log.error(f"Error fetching order book data from Bitquery: {str(e)}")

    responseTime = now_timestamp()

    #
    # Post-process
    #

    depth['timestamp'] = pandas_get_interval(freq=freq, timestamp=requestTime)[0]
    depth['requestTime'] = requestTime
    depth['responseTime'] = responseTime
    depth['symbol'] = symbol

    return depth


def start_collector_depth():
    #
    # Initialize data state, connections and listeners
    #
    App.analyzer = Analyzer(None)

    App.client = Client(api_key=App.config["api_key"], api_secret=App.config["api_secret"])

    #
    # Register schedulers
    #

    App.sched = BackgroundScheduler(daemon=False)
    #logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)

    # Add job for collecting order book data (only frequency field changes in the job creation)
    freq = App.config["collector"]["depth"]["freq"]

    if freq == "5s":
        App.sched.add_job(
            lambda: asyncio.run_coroutine_threadsafe(main_collector_depth_task(), App.loop),
            trigger='cron',
            second='*/5',
            id = 'sync_depth_collector_task'
        )
    elif freq == "1m":
        App.sched.add_job(
            lambda: asyncio.run_coroutine_threadsafe(main_collector_depth_task(), App.loop),
            trigger='cron',
            minute='*',
            id='sync_depth_collector_task'
        )
    else:
        log.error(f"Unknown frequency in app config: {freq}. Exit.")
        return

    App.sched.start()  # Start scheduler (essentially, start the thread)

    #
    # Start event loop
    #

    App.loop = asyncio.get_event_loop()
    try:
        App.loop.run_forever()  # Blocking. Run until stop() is called
    except KeyboardInterrupt:
        pass
    finally:
        print("===> Closing Loop")
        App.loop.close()
        App.sched.shutdown()

    return 0


if __name__ == "__main__":
    App.analyzer = Analyzer(None)
    App.client = Client(api_key=App.config["api_key"], api_secret=App.config["api_secret"])
    App.loop = asyncio.get_event_loop()
    try:
        App.loop.run_until_complete(main_collector_depth_task())
    except KeyboardInterrupt:
        pass
    finally:
        print("===> Closing Loop")
        App.loop.close()
        App.sched.shutdown()

    pass
