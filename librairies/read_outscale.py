from osc_sdk_python import Gateway

def read_vms():
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadVms()

    return data

def read_vm(vm):
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadVms(
        Filters={
            "VmIds": [vm],
        },
    )

    return data

def read_images():
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadVms()

    return data

def read_vpcs():
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadNets()

    return data

def read_vpc(vpc):
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadNets(
        Filters={
            "NetIds": [vpc],
        },
    )

    return data

def read_image(image):
    gw = Gateway(**{"profile": "default"})

    data = gw.ReadImages(
        Filters={
            "ImageIds": [image],
        },
    )

    return data