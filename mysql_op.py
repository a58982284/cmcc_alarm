#!/usr/bin/python
import sys
import yaml
import MySQLdb


class mysql_op(object):

    def __init__(self, host, service):
        self.host = host
        self.service = service
        self.field = "{}_alarm_raised".format(service)

    def set_alarm_indication(self):
        sql_statement = """update alarm_indication_tbl set %s = 'Y' where Host=\'%s\';""" % (self.field, self.host)
        self.mysql_update_db('ca', 'alarm_indication_tbl', sql_statement)

    def reset_alarm_indication(self):
        sql_statement = """update alarm_indication_tbl set %s = 'N' where Host=\'%s\';""" % (self.field, self.host)
        self.mysql_update_db('ca', 'alarm_indication_tbl', sql_statement)

    def get_alarm_indication(self):
        indication = """mysql ca -e \" select %s from alarm_indication_tbl where Host=\'%s\'; \" | grep -v %s""" % (
        self.field, self.host, self.field)
        print indication
        cursor.execute(indication)
        db.commit()
        db.close()

    def mysql_update_db(self, DB_name, Table_name, sql_statement):
        update_db = """mysql %s -e "LOCK TABLES %s WRITE; %s; UNLOCK TABLES;""" % (DB_name, Table_name, sql_statement)
        cursor.execute(update_db)
        db.commit()
        db.close()


if __name__ == '__main__':
    with open('/etc/astute.yaml', 'r') as f:
        info = yaml.load(f)
        mysql_vip = info['network_metadata']['vips']['management']['ipaddr']
        mysql_root_password = info['mysql']['root_password']
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    # create_dase_sql = """create database if not exists om_datafree;"""
    # use_base_sql = """use om_datafree;"""
    # create_table_sql = """create table if not exists vm_monitor (uuid varchar(50) not null, status varchar(50) not null);"""
    # cursor.execute(create_dase_sql)
    # cursor.execute(use_base_sql)
    # cursor.execute(create_table_sql)
    # db.commit()
    # db.close()
    mysql_op_instance = mysql_op(sys.argv[1], sys.argv[2])
    mysql_op_instance.set_alarm_indication()
    mysql_op_instance.reset_alarm_indication()
    mysql_op_instance.get_alarm_indication()