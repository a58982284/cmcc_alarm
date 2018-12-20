import commands
import os

# nova_list_status,nova_list=commands.getstatusoutput("nova list --all 2>/dev/null | grep ^\"|\" | grep -v ID")
# vm_uuid = nova_list.split("\n")
# print vm_uuid
# vm_uuid_status,vm_uuid=commands.getstatusoutput("%s| awk -F\"|\" '{print $2}' | tr -d ' '"%(nova_list))

# for i in nova_list:
# print(i)
# vm_uuid_status,vm_uuid=os.popen("echo \"$line\" | awk -F\"|\" '{print $2}' | tr -d ' '")
# commands.getstatusoutput("done")
# print(vm_uuid)


# '| 40b19a0d-7a19-497d-be68-2e9c194ac237 | test_vm1      | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.17             |\n| 07e7bafb-f95e-425e-a9e0-ba140e4a1556 | vm1           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.8, 10.0.29.9   ' \
# '|\n| 235cda77-5e2f-4ce3-8c4e-6f60ea4cae9d | vm2           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.12             |\n| fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | vm_raw        | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.11             ' \
# '|\n| 1c92b57d-775c-42b1-b888-f5cd0924d688 | vm_raw2       | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.14             |\n| 8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca | watchdog-test | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.18, 10.0.29.19 |')


# ['| 40b19a0d-7a19-497d-be68-2e9c194ac237 | test_vm1      | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.17             |', '| 07e7bafb-f95e-425e-a9e0-ba140e4a1556 | vm1           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.8, 10.0.29.9   |', '| 235cda77-5e2f-4ce3-8c4e-6f60ea4cae9d | vm2           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.12             |', '| fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | vm_raw        | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.11             |', '| 1c92b57d-775c-42b1-b888-f5cd0924d688 | vm_raw2       | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.14             |', '| 8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca | watchdog-test | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.18, 10.0.29.19 |']


# nova_list = ['| 40b19a0d-7a19-497d-be68-2e9c194ac237 | test_vm1      | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.17             ', ' 07e7bafb-f95e-425e-a9e0-ba140e4a1556 | vm1           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.8, 10.0.29.9   ', ' 235cda77-5e2f-4ce3-8c4e-6f60ea4cae9d | vm2           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.12             ', ' fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | vm_raw        | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.11             ', ' 1c92b57d-775c-42b1-b888-f5cd0924d688 | vm_raw2       | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.14             ', ' 8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca | watchdog-test | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.18, 10.0.29.19 |']
nova_list = [
    '| 40b19a0d-7a19-497d-be68-2e9c194ac237 | test_vm1      | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.17             ',
    ' 07e7bafb-f95e-425e-a9e0-ba140e4a1556 | vm1           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.8, 10.0.29.9   ',
    ' 235cda77-5e2f-4ce3-8c4e-6f60ea4cae9d | vm2           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.12             ',
    ' fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | vm_raw        | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.11             ',
    ' 1c92b57d-775c-42b1-b888-f5cd0924d688 | vm_raw2       | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.14             ',
    ' 8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca | watchdog-test | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.18, 10.0.29.19 |']
a = [
    '| 40b19a0d-7a19-497d-be68-2e9c194ac237 | test_vm1      | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.17             |',
    '| 07e7bafb-f95e-425e-a9e0-ba140e4a1556 | vm1           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.8, 10.0.29.9   |',
    '| 235cda77-5e2f-4ce3-8c4e-6f60ea4cae9d | vm2           | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.12             |',
    '| fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | vm_raw        | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.11             |',
    '| 1c92b57d-775c-42b1-b888-f5cd0924d688 | vm_raw2       | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.14             |',
    '| 8cca0c0c-4f36-47c9-a0c3-bd13e2b313ca | watchdog-test | 87772029bed54fb0b36bdb966b6cbd1e | ACTIVE | -          | Running     | test-2900=10.0.29.18, 10.0.29.19 |']

for i in a:

    b = i.split("|")

    vm_uuid = b[1]
    vm_uuid_split = vm_uuid.split(" ")
    vm_uuid_rel = vm_uuid_split[1]

    vm_name = b[2]

    vm_name_split = vm_name.split(" ")

    vm_name_rel = vm_name_split[1]

    vm_last_status = b[4]
    vm_last_status_split = vm_last_status.split(" ")

    vm_last_status_rel = vm_last_status_split[1]
    tenant_id = b[3]
    tenant_id_split = tenant_id.split(" ")
    tenant_id_rel = tenant_id_split[1]
    print(tenant_id_rel)
    vm_last_status_file = vm_name_rel + ',' + vm_uuid_rel + ',' + vm_last_status_rel
    #print(vm_last_status_file)

# len("40b19a0d-7a19-497d-be68-2e9c194ac237")
# len("87772029bed54fb0b36bdb966b6cbd1e")
