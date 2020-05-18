#!/usr/bin/env python

import datetime
import multiprocessing as mp
import time

import ping3
from scapy.layers.inet import traceroute

targets = {
    'Google': '8.8.8.8',
    'UTK': '160.36.0.66',
    'Local Gateway': '10.0.0.1',
    'Xfinity WAN IP': '73.120.21.182',
    'Xfinity WAN Gateway': '73.120.20.1',
    'Xfinity Primary DNS': '75.75.75.75',
    'Xfinity Secondary DNS': '75.75.76.76'
}

# In seconds
interval = 30


def run_traceroute(target_address):
    trace_output = traceroute(target_address)[0]
    return trace_output


def run_ping(target_address):
    try:
        ping_output = ping3.ping(target_address)
    except OSError:
        ping_output = None

    return ping_output


def main():
    pool = mp.Pool(processes=mp.cpu_count())

    traceroutes = open('traceroutes.txt', 'a')
    pings = open('pings.txt', 'a')
    failures = open('failures.txt', 'a')

    try:
        while True:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            traceroutes.write("--- NEW RUN --- {} ---\n".format(current_time))
            pings.write("--- NEW RUN --- {} ---\n".format(current_time))

            for target_name, target_address in targets.items():
                res = pool.apply_async(run_traceroute, (target_address,))
                trace_output = res.get()
                traceroutes.write(
                    "{} - {} - {} - {}\n".format(current_time, target_name, target_address, trace_output.get_trace()))

                res = pool.apply_async(run_ping, (target_address, ))
                ping_output = res.get()
                pings.write("{} - {} - {} - {}\n".format(current_time, target_name, target_address, ping_output))

                if len(trace_output) == 0:
                    failures.write(
                        "{} - {} - {} - {}\n".format(current_time, target_name, target_address, "Failed traceroute"))
                if not ping_output:
                    failures.write(
                        "{} - {} - {} - {}\n".format(current_time, target_name, target_address, "Failed ping"))

            traceroutes.flush()
            pings.flush()
            failures.flush()

            time.sleep(interval)
    except KeyboardInterrupt:
        traceroutes.close()
        pings.close()
        failures.close()
    finally:
        traceroutes.close()
        pings.close()
        failures.close()


if __name__ == '__main__':
    main()
