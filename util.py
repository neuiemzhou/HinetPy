#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' utility functions for HinetScripts '''

import re
import sys
import logging
import configparser

import requests

# Global variables for URLs
AUTH = 'https://hinetwww11.bosai.go.jp/auth'
CONT = AUTH + '/download/cont'
STATUS = CONT + '/cont_status.php'
SELECT = CONT + '/select_confirm.php'
STATION = CONT + '/select_info.php'
REQUEST = CONT + '/cont_request.php'
DOWNLOAD = CONT + '/cont_download.php'
JMA = AUTH + '/JMA/dlDialogue.php'


def auth_login(username, password):
    ''' login Hinet website '''

    logging.debug("Username: " + username)
    logging.debug("Password: " + password)
    auth = {
        'auth_un': username,
        'auth_pw': password,
    }

    try:
        s = requests.Session()
        s.timeout = 30
        s.verify = True
        s.get(AUTH)  # get cookies
        r = s.post(AUTH, data=auth)  # login
    except requests.exceptions.ConnectTimeout:
        logging.error("ConnectTimeout in %d seconds.", s.timeout)
        sys.exit()
    except requests.exceptions.ConnectionError:
        logging.error("Name or service not known.")
        sys.exit()

    inout = re.search(r'auth_log(?P<LOG>.*)\.png', r.text).group('LOG')
    if inout == 'out':
        logging.error("Maybe unauthorized. Check your username and password!")
        sys.exit()

    return s


def read_config(config_file):
    ''' read configure file '''

    config = configparser.ConfigParser()

    if not config.read(config_file):
        logging.error("Configure file %s not found!", config_file)
        sys.exit()

    return config


def get_station_number(s, net):
    ''' check selected number of stations of Hi-net and F-net '''

    if net == 'Hi-net':
        pattern = r'<td class="td1">(?P<CHN>N\..{3}H)<\/td>'
        max_station_number = 777
    elif net == 'F-net':
        pattern = r'<td class="td1">(?P<CHN>N\..{3}F)<\/td>'
        max_station_number = 73

    r = s.get(STATION)
    station_count = len(re.findall(pattern, r.text))
    if station_count == 0:
        station_count = max_station_number

    logging.info("Selected Stations of %s: %d", net, station_count)

    return station_count
