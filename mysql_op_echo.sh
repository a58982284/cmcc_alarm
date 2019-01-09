#mysql_op.sh
#!/bin/bash

set_alarm_indication()
{
  host=$1
  service=$2
  field=${service}_alarm_raised

  mysql_update_db ca alarm_indication_tbl "update alarm_indication_tbl set $field = 'Y' where Host='$host';"
}

reset_alarm_indication()
{
  host=$1
  service=$2
  field=${service}_alarm_raised

  mysql_update_db ca alarm_indication_tbl "update alarm_indication_tbl set $field = 'N' where Host='$host';"
}

get_alarm_indication()
{
  host=$1
  service=$2
  field=${service}_alarm_raised

  indication=`mysql ca -e " select $field from alarm_indication_tbl where Host='$host'; " | grep -v $field`

  echo $indication
}

mysql_update_db()
{
  DB_name=$1
  Table_name=$2
  sql_statement=$3

  mysql $DB_name -e "LOCK TABLES \`$Table_name\` WRITE; $sql_statement; UNLOCK TABLES;"
}
