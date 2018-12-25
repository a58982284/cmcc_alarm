#coding:utf-8

a={
   '8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca':'ACTIVE',
   '1e93894c-44b3-44ec-af1c-3de20eb3d084':'ACTIVE',
   '40b19a0d-7a19-497d-be68-2e9c194ac237':'ERROR',
   '1e93894c-4db3-44ec-af1c-3de20eb3d084':'SHUTOFF'
}
b={
    '8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca':'ERROR',
   '1e93894c-44b3-44ec-af1c-3de20eb3d084':'SHUTOFF',
   '40b19a0d-7a19-497d-be68-2e9c194ac237':'ACTIVE',
   '1e93894c-4db3-44ec-af1c-3de20eb3d084':'ACTIVE',
   '22b19a0d-7a19-497d-be68-2e9casdfa237':'ACTIVE',
   }


#print list(set(b).difference(set(a)))       #b里面有的uuid,而a里面没有的,用来追踪新增的虚拟机
#print type(a.keys())

def dictdifferent(a,b):
    pass

def dictionarIntersetction(a,b):
    dict4 = dict.fromkeys([x for x in b if x not in a ])
    print dict4
    if dict4 !={}:
        print dict4
        for key in dict4:
            print(key)
    dict3 = dict.fromkeys([x for x in a if x in b and a[x]!=b[x]])
    #print(dict3)    #{'8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca': None}
    for k in dict3:
        if a[k] =="ACTIVE" and b[k] == "ERROR":
            print('raise event -to error %s'%k)
            #print(b[k])
        if a[k] =="ACTIVE" and b[k] == "SHUTOFF":
            print('raise event -to shutoff %s'%k)
            #print(b[k])
        if a[k] == "ERROR" and b[k] == "ACTIVE":
            print('clear event -error %s'%k)
            #print(b[k])
        if a[k] == "SHUTOFF" and b[k] == "ACTIVE":
            print('clear event - shutoff %s'%k)
    return dict3

dictionarIntersetction(a,b)

print(len('8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca'))




