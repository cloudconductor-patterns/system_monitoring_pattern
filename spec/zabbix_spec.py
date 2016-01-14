#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2014-2015 TIS Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import urllib2
import json
import base64
from zabbix.api import ZabbixAPI
from distutils.version import StrictVersion

def ret_url_encode(encode_str):

    return encode_str.replace('+','%2B')

def get_kv(keystrings,token):

    import urllib2

    response = urllib2.urlopen('http://127.0.0.1:8500/v1/kv/' + keystrings + '?token=' + token)

    return response.read()

if __name__ == '__main__':

    import sys

    consul_kv = get_kv("cloudconductor/patterns/system_monitoring_pattern/attributes",ret_url_encode(os.environ['CONSUL_SECRET_KEY']))
    decode_consul_kv = json.loads(consul_kv)
    decode_user_attribute = json.loads(base64.b64decode(decode_consul_kv[0]["Value"]))
    zabbix_user = decode_user_attribute['zabbix_part']['zabbix_user']
    zabbix_password = decode_user_attribute['zabbix_part']['zabbix_password']
    zabbix_url = decode_user_attribute['zabbix_part']['zabbix_url']
    zabbix_template = decode_user_attribute['zabbix_part']['zabbix_template']

    # Getting Consul KV
    consul_kv = get_kv("cloudconductor/system_domain",ret_url_encode(os.environ['CONSUL_SECRET_KEY']))
    decode_consul_kv = json.loads(consul_kv)
    decode_user_attribute = json.loads(base64.b64decode(decode_consul_kv[0]["Value"]))
    system_domain = decode_user_attribute['dns']
    system_name = decode_user_attribute['name']

    # Create ZabbixAPI class instance
    try:
        zapi = ZabbixAPI(url=zabbix_url, user=zabbix_user, password=zabbix_password)
    except Exception, e:
        print e, 'ZabbixAPI: Authenticate failed.'

    # Get Zabbix API version
    try:
        result_version = zapi.api_version()
    except:
        result_version = "2.4"

    # Hostgroup get
    hostgroup = system_name
    try:
        result_hostgroup = zapi.do_request('hostgroup.get', { 'filter': {'name': hostgroup}})
        if not result_hostgroup['result']:
            print 'Can not be found host group ' + hostgroup
            exit (-1)
        else:
            hostgroup_id = result_hostgroup['result'][0]['groupid']
    except Exception, e:
        print e, 'ZabbixAPI: hostgroup.get exist failed.'

    # Host get
    hostname = system_domain
    try:
        result_host = zapi.do_request('host.get', { 'filter': {'name': hostname}})
        if not result_host['result']:
            print 'Can not be found host ' + hostname
            exit (-1)
    except Exception, e:
        print e, 'ZabbixAPI: host.get exist failed.'

    # Action registry
    action = 'FailOver_' + hostname
    try:
        result_action = zapi.do_request('action.get', { 'filter': {'name': action}})
        if not result_action['result']:
            print 'Can not be found action ' + action
            exit (-1)
    except Exception, e:
        print e, 'ZabbixAPI: action.get exist failed.'

    exit ()
