import re
from time import sleep
import requests
from librairies import read_outscale

http_server = 'http://localhost:8080/api'

def cmdb_read_servers(header):
    url = f'{http_server}/physical-servers'
    response = requests.get(url, headers=header)

    return response

def cmdb_read_vms(header):
    url = f'{http_server}/logical-servers'
    response = requests.get(url, headers=header)

    return response

def cmdb_read_vm(vm_id,header):
    url = f'{http_server}/logical-servers/{vm_id}'
    response = requests.get(url, headers=header)

    return response

def cmdb_update_vm(vm_id,data,header):
    url = f'{http_server}/logical-servers/{vm_id}'
    response = requests.put(url, headers=header, json=data)

    return response

def cmdb_read_clusters(header):
    url = f'{http_server}/clusters'
    response = requests.get(url, headers=header)

    return response

def cmdb_read_cluster(cluster_id,header):
    url = f'{http_server}/clusters/{cluster_id}'
    response = requests.get(url, headers=header)

    return response

def cmdb_create_clusters(data,header):
    name_to_vm_ids = {}
    url = f'{http_server}/clusters'
    extracted_data = []
    description = ""

    # 'id': 8,
    # 'name': 'o11y-managed-svc-zex-prod',
    # 'type': 'Kubernetes',
    # 'description': None,
    # 'address_ip': None,
    # 'created_at': '2025-07-31T19:46:26.000000Z',
    # 'updated_at': '2025-07-31T19:46:26.000000Z',
    # 'deleted_at': None

    for cluster in data["Vms"]:
        name_cluster = ""

        attribute_value = next((tag.get("Key") for tag in cluster.get("Tags", []) if tag.get("Value") == "owned"), None)

        if attribute_value is not None:
            attribute = attribute_value.replace("OscK8sClusterID/", "")
            name_cluster = re.sub(r'-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', '', attribute)
            description = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', attribute_value)
            if description:
                uid = description.group(0)

        if name_cluster:
            if name_cluster not in name_to_vm_ids:
                name_to_vm_ids[name_cluster] = []
            name_to_vm_ids[name_cluster].append(cluster['VmId'])

    for name_cluster, vm_ids in name_to_vm_ids.items():

        extracted_cluster = {
            "name": name_cluster,
            "type": "Kubernetes",
            "description": uid,
        }

        response = requests.post(url, headers=header, json=extracted_cluster)

        if response.status_code == 201:
            # Afficher la réponse JSON
            print(response.json())
        else:
            # Afficher le code d'erreur
            print(f"Erreur: {response.status_code}")

def cmdb_create_subnetworks(data,header):
    url = f'{http_server}/subnetworks'
    extracted_data = []

    # 'description': '<p>net-prod-std-dmz</p>',
    # 'address': '10.35.0.0/16',
    # 'ip_allocation_type': 'DHCP',
    # 'responsible_exp': None,
    # 'dmz': 'Oui',
    # 'wifi': None,
    # 'name': 'vpc-27c6ffd8',
    # 'created_at': '2025-07-30T15:27:58.000000Z',
    # 'updated_at': '2025-07-30T15:29:01.000000Z',
    # 'deleted_at': None,
    # 'connected_subnets_id': None,
    # 'gateway_id': None,
    # 'zone': 'DMZ',
    # 'vlan_id': None,
    # 'network_id': 16,
    # 'default_gateway': None
    for vpc in data["Nets"]:

        description = next((tag.get("Value") for tag in vpc.get("Tags", []) if tag.get("Key") == "Name"), None)
        zone = description.split('-')[-1]


        extracted_vpc = {
            "name": vpc["NetId"],
            "address": vpc["IpRange"],
            "ip_allocation_type": "DHCP",
            "description": description,
            "network_id": 16,
            "zone": zone,
        }
        extracted_data.append(extracted_vpc)

    for vpc in extracted_data:
        response = requests.post(url, headers=header, json=vpc)

        if response.status_code == 201:
            # Afficher la réponse JSON
            print(response.json())
        else:
            # Afficher le code d'erreur
            print(f"Erreur: {response.status_code}")

def cmdb_read_subnetworks(id,header):
    url = f'{http_server}/subnetworks/{id}'
    response = requests.get(url, headers=header)

    return response

def get_id_by_name(data, name):
    item = next((item for item in data if item['name'] == name), None)

    return item['id'] if item else None

def cmdb_create_vms(data,header):
    url = f'{http_server}/logical-servers'
    extracted_data = []

    for vm in data["Vms"]:

        public_ip = vm.get("Nics", [{}])[0].get("LinkPublicIp", {}).get("PublicIp") if vm.get("Nics") else None
        attribute_value = next((tag.get("Key") for tag in vm.get("Tags", []) if tag.get("Value") == "owned"), None)
        name_value = next((tag.get("Value") for tag in vm.get("Tags", []) if tag.get("Key") == "Name"), None)
        network_value = next((tag.get("Value") for tag in vm.get("Tags", []) if tag.get("Key") == "Network"), None)

        cluster_id = None

        # print(name_value)
        if attribute_value is not None:
            attribute = attribute_value.replace("OscK8sClusterID/", "")
            name_cluster = re.sub(r'-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', '',attribute)
            clusters_list = cmdb_read_clusters(header)
            cluster_id = get_id_by_name(clusters_list.json(),name_cluster)
        else:
            attribute = vm["PrivateDnsName"]

        name = re.sub(r'-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', '', name_value)

        image = read_outscale.read_image(vm["ImageId"])

        os = image.get("Images", [{}])[0].get("ImageName") if image.get("Images") else None

        # get CPU and RAM from the VmType
        s = vm["VmType"]
        numbers = re.findall(r'\d+', s)
        numbers = list(map(int, numbers))
        cpu = numbers[1]
        ram = numbers[2]

        # generate Json payload
        extracted_vm = {
            "name": vm["VmId"],
            "address_ip": vm["PrivateIp"],
            "environment": "production",
            "operating_system": os,
            "description": name,
            "attributes": attribute,
            "cpu": cpu,
            "memory": ram,
            "install_date": vm["CreationDate"],
            "configuration": vm["VmType"],
            "net_services": vm["NetId"],
            "type": network_value,
            "patching_frequency": 30,
            "physicalServers": 16,
            "cluster_id": cluster_id,
        }
        extracted_data.append(extracted_vm)

    # Afficher les données extraites
    for vm in extracted_data:

        # print(header)
        print(vm)
        response = requests.post(url, headers=header, json=vm)
        # response = requests.get(url, headers=header)
        sleep(1)

        if response.status_code == 201:
            # Afficher la réponse JSON
            print(response.json())
        else:
            if response.status_code == 429:
                sleep(3)
                response = requests.post(url, headers=header, json=vm)
            else:
                # Afficher le code d'erreur
                print(f"Erreur: {response.status_code}")
