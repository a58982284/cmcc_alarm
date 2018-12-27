#!/usr/bin/env python

from lxml import etree
from oslo_log import log as logging
from oslo_config import cfg
from oslo_utils import units
import six
import subprocess
import pprint, StringIO,sys,commands
import numpy
import MySQLdb

SHELL_MYSQL_PASSWORD = "grep mysql /etc/astute.yaml -A1 | grep root_password | awk '{print $2}'"
SHELL_REGION = "grep region_name /etc/watchmen/watchmen-producer.conf | cut -d'=' -f2"
SHELL_MYSQL_PASSWORD = "grep mysql /etc/astute.yaml -A1 | grep root_password | awk '{print $2}'"


def exeShellCmd(CmdStr):
  try:
    return subprocess.check_output(CmdStr, shell=True)
  except:
    return ""

def main():
    mysql_root_password = exeShellCmd(SHELL_MYSQL_PASSWORD).strip()
    mysql_vip = "{{ fuel_network.management_vip }}"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password, "watchmen")
    cursor = db.cursor()
    get_fmevent_seq = """select sequence_no from fmevent where minor_type='%s' and source like '%s';""" % (minor_id, source_keyword)
    cursor.execute(get_fmevent_seq)
    fmevent_sequence_no = cursor.fetchone()[0]

    update_fmevent_sql = """update fmevent set last_event_time='%s' where sequence_no='%s';""" %(time, fmevent_sequence_no)
    cursor.execute(update_fmevent_sql)
    update_fmevent_history_sql = """update fmevent_history set last_event_time='%s' where sequence_no='%s';""" %(time, fmevent_sequence_no)
    cursor.execute(update_fmevent_history_sql)
    db.commit()
    db.close()


if __name__ == '__main__':
  region = exeShellCmd(SHELL_REGION).split('\n')[0]
  database = sys.argv[1]
  minor_id = sys.argv[2]
  source_keyword = '%' + sys.argv[3] + '%'
  time = sys.argv[4]

  main()
