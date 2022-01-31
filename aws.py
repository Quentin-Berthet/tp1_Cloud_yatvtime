#!/usr/bin/env python3

__authors__ = ["Baptiste Coudray", "Quentin Berthet"]
__date__ = "13.10.2020"
__course__ = "Introduction to the cloud"
__description__ = "AWS Deployment"

import boto3

if __name__ == '__main__':
    ec2 = boto3.client('ec2')
    # Grab my AMI Images
    images = ec2.describe_images(Owners=['self'])
    # Grab only NetworkInterfaces with a Tag on it
    enis = ec2.describe_network_interfaces()["NetworkInterfaces"]
    enis = [eni for eni in enis if len(eni["TagSet"]) > 0]
    for image in images["Images"]:
        current_image = image["Name"].replace("YATVTIME-", "")
        # Grab NetworkInterface corresponding to the current image
        eni = [eni for eni in enis if current_image in eni["TagSet"][0]["Value"]]
        if len(eni) > 0:
            eni = eni[0]
            ec2i = boto3.resource('ec2')
            instances = ec2i.create_instances(
                DryRun=False,
                ImageId=image["ImageId"],
                MinCount=1,
                MaxCount=1,
                KeyName='amazon',
                InstanceType='t2.micro',
                NetworkInterfaces=[
                    {
                        'NetworkInterfaceId': eni["NetworkInterfaceId"],
                        "DeviceIndex": 0
                    }
                ]
            )
            if current_image == "HTTP":
                instances[0].wait_until_running()
                allocation = ec2.allocate_address(Domain='vpc')
                response = ec2.associate_address(AllocationId=allocation['AllocationId'],
                                                 InstanceId=instances[0].instance_id)
                print(f"Le site sera disponible à l'adresse : http://{allocation['PublicIp']}/")
