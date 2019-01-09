u = 'compute-1209-2.domain.tld'
a=u.split('.')[0]
#print a

u = 'http://192.168.42.28:8776/v1/%(tenant_id)s/volumes/detail'
b=u.split('%')[0]
print b

