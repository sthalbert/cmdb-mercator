from librairies.auth_mercator import header_mercator
from librairies.read_outscale import read_vms,read_vpcs
from librairies.mercator import cmdb_read_vm, cmdb_create_vms, cmdb_update_vm, cmdb_read_servers, cmdb_read_subnetworks, \
    cmdb_create_subnetworks, cmdb_read_clusters, cmdb_create_clusters
import json

header = header_mercator()

#print(header)

# result = cmdb_read_clusters(8,header)
#
# print(result)

data = read_vms()
#
# print(data)
#
clusters = cmdb_create_clusters(data,header)
result = cmdb_create_vms(data,header)

