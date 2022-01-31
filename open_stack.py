#!/usr/bin/env python3

__authors__ = ["Baptiste Coudray", "Quentin Berthet"]
__date__ = "13.10.2020"
__course__ = "Introduction to the cloud"
__description__ = "OpenStack Deployment"

import openstack


def create_connection_from_config():
    return openstack.connect(cloud="openstack")


IMAGE_NAMES = ["Frontend", "Backend", "Database"]
IMAGE_IPS = {
    "Frontend": "192.168.1.2",
    "Backend": "192.168.1.3",
    "Database": "192.168.1.4"
}
VOLUMES_IDS = {
    "Frontend": "ab62af6b-1b49-464d-b9d1-e4920824c8bd",
    "Backend": "6e486fef-7542-4604-a201-d87fa6193309",
    "Database": "e0a3ccc0-6ba4-4e2e-8602-4e9ca7616712"
}

if __name__ == '__main__':
    conn = create_connection_from_config()
    network = conn.network.find_network("yatvtime")
    flavor = conn.compute.find_flavor("m1.small")
    sgs = [conn.network.find_security_group(image_name) for image_name in IMAGE_NAMES]

    for i, image_name in enumerate(IMAGE_NAMES):
        instance = conn.compute.create_server(
            name=f"YATVTIME-{image_name}",
            flavor_id=flavor.id,
            block_device_mapping_v2=[{
                "boot_index": 0,
                "uuid": VOLUMES_IDS[image_name],
                "source_type": "volume",
                "destination_type": "volume"
            }],
            networks=[
                {
                    "uuid": network.id,
                    "fixed_ip": IMAGE_IPS[image_name]
                }
            ],
            security_groups=[{
                "name": sgs[i].name
            }],
            key_name="yatvtime"
        )
        if image_name == "Frontend":
            conn.compute.wait_for_server(instance)
            public_net = conn.network.find_network(name_or_id='public')
            floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
            conn.compute.add_floating_ip_to_server(instance, floating_ip.floating_ip_address)
            print(f"Le site web sera disponible à l'adresse : http://{floating_ip['floating_ip_address']}/")
