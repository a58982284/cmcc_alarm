#coding:utf-8
import commands
import sys
import MySQLdb
import yaml


def main():
    sequence_no = sys.argv[1]

    mysql_root_password = get_mysql_password()
    mysql_vip = "192.168.42.28"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    use_base_sql = """use om_datafree;"""
    cursor.execute(use_base_sql)
    last_event_time = """select last_event_time from fmevent_history where sequence_no=%s;""" % (sequence_no)      #查查%有没有语法错误
    cursor.execute(last_event_time)
    db.commit()
    db.close()
    commands.getstatusoutput("%s | grep -v last_event_time"% (last_event_time))

def get_mysql_password():
    with open('/etc/astute.yaml', 'r') as f:
        y = yaml.load(f)
    return y['mysql']['root_password']


if __name__ == '__main__':
    main()