#!/usr/bin/env python3

__authors__ = ["Baptiste Coudray", "Quentin Berthet"]
__date__ = "03.11.2020"
__course__ = "Introduction to the cloud"
__description__ = "Libcloud Deployment"

from libcloud.compute.drivers.openstack import OpenStackSecurityGroup
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import sys

AWS_ACCESS_KEY = "ASIAWDANWPDTU3UGG7MG"
AWS_SECRET_KEY = "gZXyNkbEAl8pjo07wOW1wNHhTHiN3/IhGpNKeDKA"
AWS_SESSION_TOKEN = "FwoGZXIvYXdzEHsaDOWYLjw+lBXOQgydniLMARFAzqh5SUsOhjodJuqzIY5+JODZFCzRDdeZ4YlAhmT8+1vIlVE8zjGWlNcCw8tbtgDJB9JXMFZMhrequeBt9I36j1rMqBlkgPkPJf3xTmDiYBh2kifvYUHsvhZroIOOzrX9l7CgLzAQs5DtPAwqht1a9uqPhtzqY59qxTpisMUlkxQ27f3foXwdIwtrl6rHg/9GcuAv2trim+nHc7PCe2/Dk3azmBWMo8wj2LaRDNtHLQr2fMTdlg1PtNg4Oy093IuTOW/oUpsThbKAISj4m4b9BTItWUQOGaVcuWLAvEyoAmWC+b2clydEAk2aHLhbLg21BT64xJOflR6xsZo/SOQg"
AWS_REGION = "us-east-1"

OPENSTACK_USER = "quentin.berthet@etu.hesge.ch"
OPENSTACK_PASSWORD = "e2bef626f1fcb8f0b5cc2590d104b10c"
OPENSTACK_PROJECT_NAME = "Coudray_Berthet"
OPENSTACK_AUTH_URL = "https://keystone.cloud.switch.ch:5000"
OPENSTACK_AUTH_VERSION = "3.x_password"
OPENSTACK_REGION = "ZH"

IMAGES_NAME = [
    "YATVTIME-HTTP", "YATVTIME-NODE", "YATVTIME-BDD",
    "Frontend", "Backend", "Database"
]

NODE_SIZE_NAME = {
    "aws": "t2.micro",
    "openstack": "m1.small",
}

if __name__ == '__main__':
    if len(sys.argv) < 2 or (sys.argv[1] != "aws" and sys.argv[1] != "openstack"):
        print(f"Usage: {sys.argv[0]} aws|openstack")
        exit(1)
    choice = sys.argv[1]
    drivers = []
    if choice == "aws":
        aws = get_driver(Provider.EC2)
        drivers.append(aws(AWS_ACCESS_KEY, AWS_SECRET_KEY, token=AWS_SESSION_TOKEN, region=AWS_REGION))
    if choice == "openstack":
        open_stack = get_driver(Provider.OPENSTACK)
        drivers.append(
            open_stack(OPENSTACK_USER, OPENSTACK_PASSWORD, api_version='2.0', ex_tenant_name=OPENSTACK_PROJECT_NAME,
                       ex_force_auth_url=OPENSTACK_AUTH_URL, ex_force_auth_version=OPENSTACK_AUTH_VERSION,
                       ex_force_service_region=OPENSTACK_REGION))
    for i, driver in enumerate(drivers):
        all_images = driver.list_images()
        my_images = [image for image in all_images if image.name in IMAGES_NAME]
        for j, image in enumerate(my_images):
            node_sizes = [node_size for driver in drivers for node_size in driver.list_sizes() if
                          node_size.name == NODE_SIZE_NAME[choice]]
            sg = [sg for sg in driver.ex_list_security_groups() if (type(sg) == str and sg == image.name) or (
                    type(sg) == OpenStackSecurityGroup and sg.name == image.name)]
            instance = driver.create_node(name=f"LC-{image.name}", size=node_sizes[0], image=image,
                                          ex_security_groups=sg)
            if choice == "aws":
                # Specific aws...
                # Bind Elastic IP
                if image.name == "YATVTIME-HTTP":
                    driver.wait_until_running([instance], ssh_interface="private_ips")
                    elastic_ip = driver.ex_allocate_address()
                    driver.ex_associate_address_with_node(instance, elastic_ip)
                    print(f"Le site web sera disponible à l'adresse : http://{elastic_ip.ip}/")
            if choice == "openstack":
                # Specific openstack...
                # Bind Floating IP
                if image.name == "Frontend":
                    fip = driver.ex_create_floating_ip()
                    driver.ex_attach_floating_ip_to_node(instance, fip)
                    print(f"Le site web sera disponible à l'adresse : http://{fip.ip_address}/")
            print(f"L'instance {image.name} a démarré...")
