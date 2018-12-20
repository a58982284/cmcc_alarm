res={
   'id':'ACTIVE',
   'id':'ACTIVE',
   'id':'ERROR',
   'id':'SHUTOFF'
}
vm_status_dict={}
for i in res:
    vm_uuid = i['id']
    #vm_name = i.get('name', '')
    vm_last_status = i.get('status', '')
    vm_status_dict[vm_uuid] = vm_last_status

print(vm_status_dict)