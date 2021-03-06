#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime, date

import pytest
import requests

from HinetPy import Client

username = "test_username"
password = "test_password"


# http://docs.pytest.org/en/latest/fixture.html
#@pytest.fixture is better, but pytest prior 2.10 doesn't support
@pytest.yield_fixture(scope="module")
def client():
    client = Client(username, password)
    client.select_stations('0101', ['N.AAKH', 'N.ABNH'])
    yield client
    client.select_stations('0101')


class TestClientLoginClass:
    """Login related tests"""
    def test_client_init_and_login_succeed(self):
        Client(username, password)

    def test_client_init_and_login_fail(self):
        """ Raise ConnectionError if requests fails. """
        with pytest.raises(requests.ConnectionError):
            Client("anonymous", "anonymous")

    def test_login_after_init(self):
        client = Client()
        client.login(username, password)


class TestClientCheckClass:
    def test_check_service_update(self, client):
        assert not client.check_service_update()

    def test_check_package_release(self, client):
        assert not client.check_package_release()

    def test_check_cmd_exists(self, client):
        assert client.check_cmd_exists()

    def test_docter(self, client):
        client.doctor()


class TestGetwaveformClass:
    def test_get_continuous_waveform_1(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 9)

        assert data == '0101_201001010000_9.cnt'
        assert os.path.exists(data)
        os.remove(data)
        assert ctable == '0101_20100101.ch'
        assert os.path.exists(ctable)
        os.remove(ctable)

    def test_get_continuous_waveform_starttime_in_string(self, client):
        data, ctable = client.get_continuous_waveform('0101', '2010-01-01T00:00', 9)

        assert data == '0101_201001010000_9.cnt'
        assert os.path.exists(data)
        os.remove(data)
        assert ctable == '0101_20100101.ch'
        assert os.path.exists(ctable)
        os.remove(ctable)

    def test_get_continuous_waveform_custom_name_1(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 1,
                                           data="customname1.cnt",
                                           ctable="customname1.ch")

        assert data == 'customname1.cnt'
        assert os.path.exists(data)
        os.remove(data)
        assert ctable == 'customname1.ch'
        assert os.path.exists(ctable)
        os.remove(ctable)

    def test_get_continuous_waveform_custom_name_2(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 1,
                                           data="customname2/customname2.cnt",
                                           ctable="customname2/customname2.ch")

        assert data == 'customname2/customname2.cnt'
        assert os.path.exists(data)
        assert ctable == 'customname2/customname2.ch'
        assert os.path.exists(ctable)
        shutil.rmtree("customname2")

    def test_get_continuous_waveform_custom_name_3(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 1,
                                           outdir="customname3")

        assert data == "customname3/0101_201001010000_1.cnt"
        assert os.path.exists(data)
        assert ctable == "customname3/0101_20100101.ch"
        assert os.path.exists(ctable)
        shutil.rmtree("customname3")

    def test_get_continuous_waveform_custom_name_4(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 1,
                                           data="customname4-cnt/test.cnt",
                                           ctable="customname4-ch/test.ch",
                                           outdir="customname4-data")

        assert data == "customname4-cnt/test.cnt"
        assert os.path.exists(data)
        assert ctable == "customname4-ch/test.ch"
        assert os.path.exists(ctable)
        shutil.rmtree("customname4-cnt")
        shutil.rmtree("customname4-ch")

    def test_get_waveform_alias(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_waveform('0101', starttime, 1)


class TestGetwaveformSpanClass:
    def test_get_continuous_waveform_wrong_span_1(self, client):
        starttime = datetime(2005, 1, 1, 0, 0)
        with pytest.raises(ValueError):
            client.get_continuous_waveform('0101', starttime, 0)

    def test_get_continuous_waveform_wrong_span_2(self, client):
        starttime = datetime(2005, 1, 1, 0, 0)
        with pytest.raises(ValueError):
            client.get_continuous_waveform('0101', starttime, -4)

    def test_get_continuous_waveform_wrong_span_3(self, client):
        starttime = datetime(2005, 1, 1, 0, 0)
        with pytest.raises(TypeError):
            client.get_continuous_waveform('0101', starttime, 2.5)

    def test_get_continuous_waveform_span_larger_than_int(self, client):
        starttime = datetime(2005, 1, 1, 0, 0)
        with pytest.raises(ValueError):
            client.get_continuous_waveform('0101', starttime, 400000)

    def test_get_continuous_waveform_larger_max_span(self, client):
        starttime = datetime(2010, 1, 1, 0, 0)
        data, ctable = client.get_continuous_waveform('0101', starttime, 10, max_span=65)
        assert data == '0101_201001010000_10.cnt'
        assert os.path.exists(data)
        os.remove(data)
        assert ctable == '0101_20100101.ch'
        assert os.path.exists(ctable)
        os.remove(ctable)

    def test_get_continuous_waveform_wrong_starttime(self, client):
        starttime = datetime(2001, 1, 1, 0, 0)
        with pytest.raises(ValueError):
            client.get_continuous_waveform('0101', starttime, 1)


class TestGetCatalogClass:
    def test_get_arrivaltime_1(self, client):
        startdate = date(2010, 1, 1)
        data = client.get_arrivaltime(startdate, 5)
        assert data == 'measure_20100101_5.txt'
        assert os.path.exists(data)
        os.remove(data)

    def test_get_arrivaltime_2(self, client):
        startdate = date(2010, 1, 1)
        data = client.get_arrivaltime(startdate, 5, filename="arrivaltime.txt")
        assert data == "arrivaltime.txt"
        assert os.path.exists(data)
        os.remove(data)

    def test_get_arrivaltime_use_datetime(self, client):
        startdate = datetime(2010, 1, 1)
        data = client.get_arrivaltime(startdate, 5)
        assert data == 'measure_20100101_5.txt'
        assert os.path.exists(data)
        os.remove(data)

    def test_get_arrivaltime_startdate_in_string(self, client):
        data = client.get_arrivaltime('20100101', 5)
        assert data == 'measure_20100101_5.txt'
        assert os.path.exists(data)
        os.remove(data)

    def test_get_focalmechanism_1(self, client):
        startdate = date(2010, 1, 1)
        data = client.get_focalmechanism(startdate, 5)
        assert data == 'mecha_20100101_5.txt'
        assert os.path.exists(data)
        os.remove(data)

    def test_get_focalmachanism_2(self, client):
        startdate = date(2010, 1, 1)
        data = client.get_focalmechanism(startdate, 5, filename="focal.txt")
        assert data == "focal.txt"
        assert os.path.exists(data)
        os.remove(data)

    def test_get_focalmachanism_use_datetime(self, client):
        startdate = datetime(2010, 1, 1)
        data = client.get_focalmechanism(startdate, 5, filename="focal.txt")
        assert data == "focal.txt"
        assert os.path.exists(data)
        os.remove(data)

    def test_get_catalog_wrong_span(self, client):
        startdate = date(2010, 1, 1)
        with pytest.raises(ValueError):
            data = client.get_arrivaltime(startdate, 10)

    def test_get_event_waveform(self, client):
        client.get_event_waveform('201001010000', '201001020000',
                                  minmagnitude=3.5, maxmagnitude=5.5,
                                  mindepth=0, maxdepth=70,
                                  minlatitude=40.0,
                                  minlongitude=140.0,
                                  latitude=46.49,
                                  longitude=151.97,
                                  maxradius=1.0)
        assert os.path.exists("D20100101000189_20/D20100101000189_20.evt")
        shutil.rmtree("D20100101000189_20")


class TestClientGetStationList:

    def test_get_station_list(self, client):
        stations = client.get_station_list('0101')
        assert type(stations) == list
        assert len(stations) >= 700

        stations = client.get_station_list('0120')
        assert type(stations) == list
        assert len(stations) >= 120

        stations = client.get_station_list('0131')
        assert type(stations) == list
        assert len(stations) >= 250


class TestClientOthersClass:

    def test_get_allowed_span(self, client):
        assert client._get_allowed_span('0401') == 60
        client.select_stations('0101')
        assert client._get_allowed_span('0101') == 5
        client.select_stations('0101', ['N.AAKH', 'N.ABNH'])
        assert client._get_allowed_span('0101') == 60

    def test_get_selected_stations(self, client):
        client.get_selected_stations('0101')
        client.get_selected_stations('0103')
        with pytest.raises(ValueError):
            client.get_selected_stations('0501')

    def test_get_win32tools(self, client):
        assert client._get_win32tools() == "win32tools.tar.gz"
        os.remove("win32tools.tar.gz")
