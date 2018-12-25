#coding:utf-8
def  mysql_crud(statement):
    mysql_root_password = get_mysql_password()  #commit mysql
    mysql_vip = "192.168.42.28"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    create_dase_sql = """create database if not exists om_datafree;"""
    cursor.execute(create_dase_sql)
    use_base_sql = """use om_datafree;"""
    cursor.execute(use_base_sql)
    create_table_sql = """create table if not exists vm_monitor (vm_uuid varchar(128) not null unique, vm_status varchar(32)) ENGINE=InnoDB;"""
    cursor.execute(create_table_sql)
    #insert_sql = """insert ignore into vm_monitor values(\'%s\',\'%s\');""" % (vm_uuid, vm_last_status)  # 往数据库插入数据
    insert_sql = """%s"""%statement
    print(insert_sql)
    cursor.execute(insert_sql)
    db.commit()
    db.close()

mysql_crud("""insert ignore into vm_monitor values(\'%s\',\'%s\');""" % ('', ''))