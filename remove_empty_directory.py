#coding:utf-8
import commands
import sys
import MySQLdb
import yaml
import os


def main():
    dir = sys.argv[1]
    exists_dir_status,exists_dir=commands.getstatusoutput("[ ! -d %s ] &&  exit 0"%(dir))
    status,output=commands.getstatusoutput("find %s -type f 2>/dev/null  | wc -l"%(dir))
    if output == 0:
        commands.getstatusoutput("rm -rf %s"%(dir))

if __name__ == '__main__':
    main()