import MySQLdb
import yaml


def get_mysql_password():
    with open('/etc/astute.yaml', 'r') as f:
        y = yaml.load(f)
    return y['mysql']['root_password']


if __name__ == '__main__':
    mysql_root_password = get_mysql_password()
    mysql_vip = "{{ fuel_network.management_vip }}"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    select_db_sql = """SELECT * FROM information_schema.SCHEMATA where SCHEMA_N                                                                                      AME='om_datafree';"""
    db_exist = cursor.execute(select_db_sql)
    if db_exist == 0:
        create_dase_sql = """create database if not exists om_datafree;"""
        cursor.execute(create_dase_sql)
    use_base_sql = """use om_datafree;"""
    cursor.execute(use_base_sql)
    create_table_sql = """create table if not exists traffic_link_flag (compute                                                                                      _name varchar(20) not null, flag int default 0 not null);"""
    cursor.execute(create_table_sql)
    db.commit()
    db.close()
