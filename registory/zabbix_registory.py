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

def load_yaml(yaml_file):
    import yaml

    with open('config/' + yaml_file) as reader:
        return yaml.load(reader.read())

def host_create_params(hostname, hostgroupid, template_id):

    ret_parameters = {
        'host': hostname,
        'interfaces': [
            {
                'type': 1,
                'main': 1,
                'ip': '',
                'dns': hostname,
                'port': 10050,
                'useip': 0
            }
        ],
        'groups': [
            {
                'groupid': hostgroup_id
            }
        ],
        'templates': [
            {
                'templateid': template_id
            }
        ]
    }
    return ret_parameters

def action_create_params(action, host_id, operation, version):

    if StrictVersion(version) >= StrictVersion("2.4"):
        ret_parameters = {
            'name': action,
            'eventsource': 0,
            'status': 0, # enabled
            'esc_period': 120,
            'def_shortdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}',
            'def_longdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}',
            'operations': generate_operations(operation),
            'filter': {
                'evaltype': 1, # AND
                'conditions': generate_conditions(host_id)
            }
    }
    else:
        ret_parameters = { 'name': action,
            'eventsource': 0,
            'status': 0, # enabled
            'esc_period': 120,
            'def_shortdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}',
            'def_longdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}',
            'operations': generate_operations(operation),
            'evaltype': 1, # AND
            'conditions': generate_conditions(host_id)
        }

    return ret_parameters

def generate_conditions(host_id):

    ret_parameters = [
        {
            'conditiontype': '1', # host
            'operator': '0', # equal
            'value': host_id
        },
        {
            'conditiontype': '5', # trigger value
            'operator': '0', # equal
            'value': '1'
        }
    ]

    return ret_parameters

def generate_operations(operation):

    ret_parameters = [
        {
            "operationtype": "1", # remote command
            "opcommand_hst": {
                "hostid": "0"
            },
            "opcommand": {
                "type": "0", # custom script
                "command": operation,
                "execute_on": "1" # Zabbix server
            }
        }
    ]

    return ret_parameters

def operation(environment_id ,auth_token, url):

    parameter = '\'{"switch": "true", "auth_token": "' + auth_token + '"}\''
    ret_parameters = 'curl -H "Content-Type:application/json" -X POST -d ' + parameter + ' ' + url.rstrip('/') + '/api/v1/environments/' + str(environment_id) + '/rebuild'

    return ret_parameters

if __name__ == '__main__':

    import sys

    # Settings Yaml
    # ex. yaml_data = load_yaml('monitoring.yml')

    # Settings Json
    consul_kv = get_kv("cloudconductor/patterns/system_monitoring_pattern/attributes",ret_url_encode(os.environ['CONSUL_SECRET_KEY']))
    decode_consul_kv = json.loads(consul_kv)
    decode_user_attribute = json.loads(base64.b64decode(decode_consul_kv[0]["Value"]))
    cloudconductor_url = decode_user_attribute['common']['cloudconductor_url']
    cloudconductor_token = decode_user_attribute['common']['cloudconductor_auth_token']
    zabbix_user = decode_user_attribute['zabbix_part']['zabbix_user']
    zabbix_password = decode_user_attribute['zabbix_part']['zabbix_password']
    zabbix_url = decode_user_attribute['zabbix_part']['zabbix_url']
    zabbix_template = decode_user_attribute['zabbix_part']['zabbix_template']

    # Getting Consul KV
    consul_kv = get_kv("cloudconductor/environment_id",ret_url_encode(os.environ['CONSUL_SECRET_KEY']))
    decode_consul_kv = json.loads(consul_kv)
    decode_user_attribute = json.loads(base64.b64decode(decode_consul_kv[0]["Value"]))
    environment_id = decode_user_attribute['environment_id']

    consul_kv = get_kv("cloudconductor/system_domain",ret_url_encode(os.environ['CONSUL_SECRET_KEY']))
    decode_consul_kv = json.loads(consul_kv)
    decode_user_attribute = json.loads(base64.b64decode(decode_consul_kv[0]["Value"]))

    try:
        system_domain = decode_user_attribute['dns']
    except Exception, w:
        system_domain = 'localhost'
        print w, 'Please dns name change the settings as soon as possible.'

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

    # Hostgroup create
    hostgroup = system_name
    try:
        result_hostgroup = zapi.do_request('hostgroup.get', { 'filter': {'name': hostgroup}})
        if not result_hostgroup['result']:
            result_hostgroup = zapi.do_request('hostgroup.create', {'name': hostgroup})
            hostgroup_id = result_hostgroup['result']['groupids'][0]
        else:
            hostgroup_id = result_hostgroup['result'][0]['groupid']
    except Exception, e:
        print e, 'ZabbixAPI: Hostgroup exist failed.'

    # Host create
    hostname = system_domain
    try:
        result_host = zapi.do_request('host.get', { 'filter': {'name': hostname}})
        result_template = zapi.do_request('template.get', { 'filter': {'host': zabbix_template}})
        if not result_host['result']:
            result_host = zapi.do_request('host.create', host_create_params(hostname, hostgroup_id, result_template['result'][0]['templateid']))
            host_id = result_host['result']['hostids'][0]
        else:
            host_id = result_host['result'][0]['hostid']
    except Exception, e:
        print e, 'ZabbixAPI: Host exist failed.'

    # Action registry
    action = 'FailOver_' + hostname
    try:
        result_action = zapi.do_request('action.get', { 'filter': {'name': action}})
        if str(result_action['result']) == '[]':
            result_action = zapi.do_request('action.create', action_create_params(action,host_id, operation(environment_id, cloudconductor_token, cloudconductor_url),result_version))
    except Exception, e:
        print e, 'ZabbixAPI: Action exist failed.'

    exit (0)
