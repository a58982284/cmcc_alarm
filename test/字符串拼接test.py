#coding:utf-8
vm_uuid = "fb5b124a-8bd2-4faf-b50b-64ca64fe5c78"


a = "nova show %s | grep hypervisor_hostname | awk -F\"|\" '{print $3}' | tr -d ' '"%(vm_uuid)

print(a)

#命令得到的结果是:compute-1209-2.domain.tld

'''
root@cic-1:~# ping -c 1 compute-1209-2.domain.tld
PING compute-1209-2.domain.tld (192.168.42.20) 56(84) bytes of data.
64 bytes from compute-1209-2.domain.tld (192.168.42.20): icmp_seq=1 ttl=64 time=1.46 ms

--- compute-1209-2.domain.tld ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.460/1.460/1.460/0.000 ms

'''
'''
root@cic-1:~# nova show fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | grep status | grep -v host_status | awk -F "|" '{print $3}' | tr -d ' '
ERROR
'''