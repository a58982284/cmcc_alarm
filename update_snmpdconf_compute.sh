#!/bin/bash

set -eu

ipaddr=$(ifconfig br-mgmt | grep "inet addr" | cut -d : -f 2 | cut -d ' ' -f 1)

sed -i "s/udp:127.0.0.1/udp:$ipaddr/g" /etc/snmp/snmpd.conf
sed -i 's/.1.3.6.1.2.1.25.1/.1.3.6.1.4.1.2021/g' /etc/snmp/snmpd.conf
sed -i 's/.1.3.6.1.2.1.1/.1.3.6.1.2.1/g' /etc/snmp/snmpd.conf
