About
=====

This is the optional pattern designed to disaster recovery which monitoring provides to platform less patterns.
Currently supported oparationg system:

* CentOS (6.7 7.2)

Currently supported monitoring software:

* Zabbix (2.2 3.0)

For more information, please visit [official web site](http://cloudconductor.org/).

Requirements
============

Prerequisites
-------------

- cloudconductor (>= 2.0)
- any platform pattern

How to use patterns
============

You can apply this pattern by using CloudConductor CLI tools or REST API.
Please see [Getting started](http://cloudconductor.org/en/documents/getting-started) in official web site to know
how the parameters you input to CloudConductor CLI tools or REST API are converted into
chef attributes.

Attributes
==========

The attributes not described here have default values, and you can change the value of them if you need.
Please see the attribute files if you want to know what kind of attributes are in this pattern.

- Attribute

| Attribute             | Value                                           |
| -------------------- |:------------------------------------------------ |
| cloudconductor_url   | Cloudconductor grobal address (port)             |
| cloudconductor_auth_token | Cloudconductor accsess secret key                |
| zabbix_url           | zabbix-web front address                         |
| zabbix_user          | zabbix usertype: Zabbix Admin and RW Permissions |
| zabbix_password      | zabbix password                                  |
| zabbix_template      | Attach Zabbix template to created host           |

sample) config/environment_attribute.json.smp

```config/environment_attribute.json.smp
{
  "system_monitoring_pattern": {
    "common": {
      "cloudconductor_url": "[[CLOUDCONDUCTOR_URL[:8080]]]",
      "cloudconductor_auth_token: "[[CLOUDCONDUCTOR_TOKEN]]"
    },
    "zabbix_part": {
      "zabbix_url": "http://[[ZABBIX.ADDRESS]]/zabbix",
      "zabbix_user": "[[USERNAME]]",
      "zabbix_password": "[[PASSWORD]]",
      "zabbix_template": "Template App HTTP Service"
    }
  }
}
```

- How to

Please be sure to specify the domain when you create a system
  `cc-cli system create --project sample_project --name dr-pattern --description "disaster recovery pattern" --domain "disaster.sampledomain.com"`

  `cc-cli environment create --system sample_system --blueprint sample_blueprint --clouds cloud-aws --name sample_environment --version 1 --user-attribute-file ~/environment_attribute.json`


Copyright and License
=====================

Copyright 2016 TIS inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Contact
========

For more information: <http://cloudconductor.org/>

Report issues and requests: <https://github.com/cloudconductor-patterns/system_monitoring_pattern/issues>

Send feedback to: <ccndctr@gmail.com>
