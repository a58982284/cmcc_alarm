import commands

status, output = commands.getstatusoutput("pgrep cpu_occupy")

commands.getstatusoutput("kill -9 {}".format(output))