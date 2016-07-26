#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_ami
version_added: "1.3"
short_description: create or destroy an image in ec2
description:
     - Creates or deletes ec2 images.
options:
  instance_id:
    description:
      - instance id of the image to create
    required: false
    default: null
  name:
    description:
      - The name of the new image to create
    required: false
    default: null
  wait:
    description:
      - wait for the AMI to be in state 'available' before returning.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
  wait_timeout:
    description:
      - how long before wait gives up, in seconds
    default: 300
  state:
    description:
      - create or deregister/delete image
    required: false
    default: 'present'
  description:
    description:
      - An optional human-readable string describing the contents and purpose of the AMI.
    required: false
    default: null
  no_reboot:
    description:
      - An optional flag indicating that the bundling process should not attempt to shutdown the instance before bundling. If this flag is True, the responsibility of maintaining file system integrity is left to the owner of the instance. The default choice is "no".
    required: false
    default: no
    choices: [ "yes", "no" ]
  image_id:
    description:
      - Image ID to be deregistered.
    required: false
    default: null
  device_mapping:
    version_added: "2.0"
    description:
      - An optional list of device hashes/dictionaries with custom configurations (same block-device-mapping parameters)
      - "Valid properties include: device_name, volume_type, size (in GB), delete_on_termination (boolean), no_device (boolean), snapshot_id, iops (for io1 volume_type)"
    required: false
    default: null
  delete_snapshot:
    description:
      - Whether or not to delete snapshots when deregistering AMI.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
  tags:
    description:
      - a dictionary of tags to add to the new image; '{"key":"value"}' and '{"key":"value","key":"value"}'
    required: false
    default: null
    version_added: "2.0"
  launch_permissions:
    description:
      - Users and groups that should be able to launch the ami. Expects dictionary with a key of user_ids and/or group_names. user_ids should be a list of account ids. group_name should be a list of groups, "all" is the only acceptable value currently.
    required: false
    default: null
    version_added: "2.0"
  image_location:
    description:
      - Full path to your AMI manifest in Amazon S3 storage. Only used for S3-based AMI's.
    required: false
    default: null
    version_added: "2.2"
  action:
    description:
      - Whether the ami should be created or registered.
    choices: [ "create", "register" ]
    required: true
    default: create
    version_added: "2.2"
  architecture:
    description:
      - The architecture of the AMI.
    choices: [ "i386", "x86_64" ]
    required: true
    default: x86_64
    version_added: "2.2"
  kernel_id:
    description:
      - The ID of the kernel with which to launch the instances
    required: false
    default: null
    version_added: "2.2"
  root_device_name:
    description:
      - The root device name (e.g. C(/dev/sda1))
    required: false
    default: null
    version_added: "2.2"
  virtualization_type:
    description:
      - The type of virtualization to use for this image of the image.
    choices: [ "hvm", "paravirtual" ]
    required: true
    default: hvm
    version_added: "2.2"
  sriov_net_support:
    description:
      - Advanced networking support. Set to simple to enable enhance networking with the Intel 82599 Virtual Function interface image. This option is supported only for C(virtualization_type=hvm) AMIs. Specifying this option with a PV AMI can make instances launched from the AMI unreachable.
    choices: [ None, "simple" ]
    required: false
    default: null
    version_added: "2.2"
  snapshot_id:
    description:
      - A snapshot ID for the snapshot to be used as root device for the image. Mutually exclusive with device_mapping, requires root_device_name
    required: false
    default: null
    version_added: "2.2"
  delete_root_volume_on_termination:
    description:
      - Whether to delete the root volume of the image after instance termination. Only applies when creating image from snapshot_id. Defaults to False. Note that leaving volumes behind after instance termination is not free.
    required: false
    default: null
    version_added: "2.2"

author:
  - "Evan Duffield (@scicoin-project) <eduffield@iacquire.com>"
  - "Constantin Bugneac (@Constantin07) <constantin.bugneac@endava.com>"
  - "Mike Buzzetti (@jimbydamonk) <mike.buzzetti@gmail.com>"

extends_documentation_fragment:
    - aws
    - ec2
'''

# Thank you to iAcquire for sponsoring development of this module.

EXAMPLES = '''
# Basic AMI Creation
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    instance_id: i-xxxxxx
    wait: yes
    name: newtest
    tags:
      Name: newtest
      Service: TestService
  register: instance

# Basic AMI Creation, without waiting
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    region: xxxxxx
    instance_id: i-xxxxxx
    wait: no
    name: newtest
  register: instance

# AMI Creation, with a custom root-device size and another EBS attached
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    instance_id: i-xxxxxx
    name: newtest
    device_mapping:
        - device_name: /dev/sda1
          size: XXX
          delete_on_termination: true
          volume_type: gp2
        - device_name: /dev/sdb
          size: YYY
          delete_on_termination: false
          volume_type: gp2
  register: instance

# AMI Creation, excluding a volume attached at /dev/sdb
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    instance_id: i-xxxxxx
    name: newtest
    device_mapping:
        - device_name: /dev/sda1
          size: XXX
          delete_on_termination: true
          volume_type: gp2
        - device_name: /dev/sdb
          no_device: yes
  register: instance

# Register AMI from snapshot
- ec2_ami:
    action: register
    virtualization_type: hvm
    root_device_name: /dev/sda1
    snapshot_id: snap-xxxxxx
    name: newtest
    region: xxxxxx

# Deregister/Delete AMI (keep associated snapshots)
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    region: xxxxxx
    image_id: "{{ instance.image_id }}"
    delete_snapshot: False
    state: absent

# Deregister AMI (delete associated snapshots too)
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    region: xxxxxx
    image_id: "{{ instance.image_id }}"
    delete_snapshot: True
    state: absent

# Update AMI Launch Permissions, making it public
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    region: xxxxxx
    image_id: "{{ instance.image_id }}"
    state: present
    launch_permissions:
      group_names: ['all']

# Allow AMI to be launched by another account
- ec2_ami:
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    region: xxxxxx
    image_id: "{{ instance.image_id }}"
    state: present
    launch_permissions:
      user_ids: ['123456789012']
'''

RETURN = '''
architecture:
    description: architecture of image
    returned: when AMI is created or already exists
    type: string
    sample: "x86_64"
block_device_mapping:
    description: block device mapping associated with image
    returned: when AMI is created or already exists
    type: a dictionary of block devices
    sample: {
        "/dev/sda1": {
            "delete_on_termination": true,
            "encrypted": false,
            "size": 10,
            "snapshot_id": "snap-1a03b80e7",
            "volume_type": "standard"
        }
    }
creationDate:
    description: creation date of image
    returned: when AMI is created or already exists
    type: string
    sample: "2015-10-15T22:43:44.000Z"
description:
    description: description of image
    returned: when AMI is created or already exists
    type: string
    sample: "nat-server"
hypervisor:
    description: type of hypervisor
    returned: when AMI is created or already exists
    type: string
    sample: "xen"
is_public:
    description: whether image is public
    returned: when AMI is created or already exists
    type: bool
    sample: false
location:
    description: location of image
    returned: when AMI is created or already exists
    type: string
    sample: "315210894379/nat-server"
name:
    description: ami name of image
    returned: when AMI is created or already exists
    type: string
    sample: "nat-server"
owner_id:
    description: owner of image
    returned: when AMI is created or already exists
    type: string
    sample: "435210894375"
platform:
    description: plaform of image
    returned: when AMI is created or already exists
    type: string
    sample: null
root_device_name:
    description: root device name of image
    returned: when AMI is created or already exists
    type: string
    sample: "/dev/sda1"
root_device_type:
    description: root device type of image
    returned: when AMI is created or already exists
    type: string
    sample: "ebs"
state:
    description: state of image
    returned: when AMI is created or already exists
    type: string
    sample: "available"
tags:
    description: a dictionary of tags assigned to image
    returned: when AMI is created or already exists
    type: dictionary of tags
    sample: {
        "Env": "devel",
        "Name": "nat-server"
    }
virtualization_type:
    description: image virtualization type
    returned: when AMI is created or already exists
    type: string
    sample: "hvm"
snapshots_deleted:
    description: a list of snapshot ids deleted after deregistering image
    returned: after AMI is deregistered, if 'delete_snapshot' is set to 'yes'
    type: list
    sample: [
        "snap-fbcccb8f",
        "snap-cfe7cdb4"
    ]
'''

import sys
import time

try:
    import boto
    import boto.ec2
    from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


def get_block_device_mapping(image):
    """
    Retrieves block device mapping from AMI
    """

    bdm_dict = dict()

    if image is not None and hasattr(image, 'block_device_mapping'):
        bdm = getattr(image,'block_device_mapping')
        for device_name in bdm.keys():
            bdm_dict[device_name] = {
                'size': bdm[device_name].size,
                'snapshot_id': bdm[device_name].snapshot_id,
                'volume_type': bdm[device_name].volume_type,
                'encrypted': bdm[device_name].encrypted,
                'delete_on_termination': bdm[device_name].delete_on_termination
            }

    return bdm_dict


def get_ami_info(image):

    return dict(
        image_id=image.id,
        state=image.state,
        architecture=image.architecture,
        block_device_mapping=get_block_device_mapping(image),
        creationDate=image.creationDate,
        description=image.description,
        hypervisor=image.hypervisor,
        is_public=image.is_public,
        location=image.location,
        ownerId=image.ownerId,
        root_device_name=image.root_device_name,
        root_device_type=image.root_device_type,
        tags=image.tags,
        virtualization_type = image.virtualization_type
    )


def create_image(module, ec2):
    """
    Creates new AMI

    module : AnsibleModule object
    ec2: authenticated ec2 connection object
    """

    instance_id = module.params.get('instance_id')
    name = module.params.get('name')
    snapshot_id = module.params.get('snapshot_id')
    root_device_name = module.params.get('root_device_name')
    kernel_id = module.params.get('kernel_id')
    virtualization_type = module.params.get('virtualization_type')
    image_location = module.params.get('image_location')
    delete_root_volume_on_termination = module.params.get('delete_root_volume_on_termination')
    sriov_net_support = module.params.get('sriov_net_support')
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))
    description = module.params.get('description')
    no_reboot = module.params.get('no_reboot')
    device_mapping = module.params.get('device_mapping')
    tags =  module.params.get('tags')
    launch_permissions = module.params.get('launch_permissions')

    try:
        params = {'instance_id': instance_id,
                  'name': name,
                  'description': description,
                  'no_reboot': no_reboot}

        register_params = {'snapshot_id': snapshot_id,
                           'root_device_name': root_device_name,
                           'kernel_id': kernel_id,
                           'virtualization_type': virtualization_type,
                           'name': name,
                           'image_location': image_location,
                           'delete_root_volume_on_termination': delete_root_volume_on_termination,
                           'sriov_net_support': sriov_net_support}

        images = ec2.get_all_images(filters={'name': name})

        if images and images[0]:
            module.exit_json(msg="AMI name already present", image_id=images[0].id, state=images[0].state, changed=False)

        if device_mapping:
            bdm = BlockDeviceMapping()
            for device in device_mapping:
                if 'device_name' not in device:
                    module.fail_json(msg = 'Device name must be set for volume')
                device_name = device['device_name']
                del device['device_name']
                bd = BlockDeviceType(**device)
                bdm[device_name] = bd
            params['block_device_mapping'] = bdm
            register_params['block_device_mapping'] = bdm

        if instance_id:
            image_id = ec2.create_image(**params)
        if snapshot_id:
            image_id = ec2.register_image(**register_params)

    except boto.exception.BotoServerError as e:
        module.fail_json(msg="%s: %s" % (e.error_code, e.error_message))

    # Wait until the image is recognized. EC2 API has eventual consistency,
    # such that a successful CreateImage API call doesn't guarantee the success
    # of subsequent DescribeImages API call using the new image id returned.
    for i in range(wait_timeout):
        try:
            img = ec2.get_image(image_id)

            if img.state == 'available':
                break
        except boto.exception.EC2ResponseError as e:
            if ('InvalidAMIID.NotFound' not in e.error_code and 'InvalidAMIID.Unavailable' not in e.error_code) and wait and i == wait_timeout - 1:
                module.fail_json(msg="Error while trying to find the new image. Using wait=yes and/or a longer wait_timeout may help. %s: %s" % (e.error_code, e.error_message))
        finally:
            time.sleep(1)

    if img.state != 'available':
        module.fail_json(msg="Error while trying to find the new image. Using wait=yes and/or a longer wait_timeout may help.")

    if tags:
        try:
            ec2.create_tags(image_id, tags)
        except boto.exception.EC2ResponseError as e:
            module.fail_json(msg = "Image tagging failed => %s: %s" % (e.error_code, e.error_message))
    if launch_permissions:
        try:
            img = ec2.get_image(image_id)
            img.set_launch_permissions(**launch_permissions)
        except boto.exception.BotoServerError as e:
            module.fail_json(msg="%s: %s" % (e.error_code, e.error_message), image_id=image_id)

    module.exit_json(msg="AMI creation operation complete", changed=True, **get_ami_info(img))


def deregister_image(module, ec2):
    """
    Deregisters AMI
    """

    image_id = module.params.get('image_id')
    delete_snapshot = module.params.get('delete_snapshot')
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))

    img = ec2.get_image(image_id)
    if img == None:
        module.fail_json(msg = "Image %s does not exist" % image_id, changed=False)

    # Get all associated snapshot ids before deregistering image otherwise this information becomes unavailable
    snapshots = []
    if hasattr(img, 'block_device_mapping'):
        for key in img.block_device_mapping:
            snapshots.append(img.block_device_mapping[key].snapshot_id)

    # When trying to re-delete already deleted image it doesn't raise an exception
    # It just returns an object without image attributes
    if hasattr(img, 'id'):
        try:
            params = {'image_id': image_id,
                      'delete_snapshot': delete_snapshot}
            res = ec2.deregister_image(**params)
        except boto.exception.BotoServerError as e:
            module.fail_json(msg = "%s: %s" % (e.error_code, e.error_message))
    else:
        module.exit_json(msg = "Image %s has already been deleted" % image_id, changed=False)

    # wait here until the image is gone
    img = ec2.get_image(image_id)
    wait_timeout = time.time() + wait_timeout
    while wait and wait_timeout > time.time() and img is not None:
        img = ec2.get_image(image_id)
        time.sleep(3)
    if wait and wait_timeout <= time.time():
        # waiting took too long
        module.fail_json(msg = "timed out waiting for image to be deregistered/deleted")

    # Boto library has hardcoded the deletion of the snapshot for the root volume mounted as '/dev/sda1' only
    # Make it possible to delete all snapshots which belong to image, including root block device mapped as '/dev/xvda'
    if delete_snapshot:
        try:
            for snapshot_id in snapshots:
                ec2.delete_snapshot(snapshot_id)
        except boto.exception.BotoServerError as e:
            if e.error_code == 'InvalidSnapshot.NotFound':
                # Don't error out if root volume snapshot was already deleted as part of deregister_image
                pass
        module.exit_json(msg="AMI deregister/delete operation complete", changed=True, snapshots_deleted=snapshots)
    else:
        module.exit_json(msg="AMI deregister/delete operation complete", changed=True)


def update_image(module, ec2):
    """
    Updates AMI
    """

    image_id = module.params.get('image_id')
    launch_permissions = module.params.get('launch_permissions')
    if 'user_ids' in launch_permissions:
        launch_permissions['user_ids'] = [str(user_id) for user_id in launch_permissions['user_ids']]

    img = ec2.get_image(image_id)
    if img == None:
        module.fail_json(msg = "Image %s does not exist" % image_id, changed=False)

    try:
        set_permissions = img.get_launch_permissions()
        if set_permissions != launch_permissions:
            if ('user_ids' in launch_permissions and launch_permissions['user_ids']) or ('group_names' in launch_permissions and launch_permissions['group_names']):
                res = img.set_launch_permissions(**launch_permissions)
            elif ('user_ids' in set_permissions and set_permissions['user_ids']) or ('group_names' in set_permissions and set_permissions['group_names']):
                res = img.remove_launch_permissions(**set_permissions)
            else:
                module.exit_json(msg="AMI not updated", launch_permissions=set_permissions, changed=False)
            module.exit_json(msg="AMI launch permissions updated", launch_permissions=launch_permissions, set_perms=set_permissions, changed=True)
        else:
            module.exit_json(msg="AMI not updated", launch_permissions=set_permissions, changed=False)

    except boto.exception.BotoServerError as e:
        module.fail_json(msg = "%s: %s" % (e.error_code, e.error_message))

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            action = dict(default='create'),
            instance_id = dict(),
            snapshot_id = dict(),
            root_device_name = dict(),
            kernel_id = dict(),
            virtualization_type = dict(),
            image_location = dict(),
            architecture = dict(default='x86_64'),
            delete_root_volume_on_termination = dict(type='bool', default=False),
            sriov_net_support = dict(),
            image_id = dict(),
            delete_snapshot = dict(default=False, type='bool'),
            name = dict(),
            wait = dict(type='bool', default=False),
            wait_timeout = dict(default=900),
            description = dict(default=""),
            no_reboot = dict(default=False, type='bool'),
            state = dict(default='present'),
            device_mapping = dict(type='list'),
            tags = dict(type='dict'),
            launch_permissions = dict(type='dict')
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    try:
        ec2 = ec2_connect(module)
    except Exception as e:
        module.fail_json(msg="Error while connecting to aws: %s" % str(e))

    if module.params.get('state') == 'absent':
        if not module.params.get('image_id'):
            module.fail_json(msg='image_id needs to be an ami image to registered/delete')

        deregister_image(module, ec2)

    elif module.params.get('state') == 'present':
        if module.params.get('image_id') and module.params.get('launch_permissions'):
            # Update image's launch permissions
            update_image(module, ec2)

        if module.params.get('action') not in ['create','register']:
            module.fail_json(msg='action must be create or register')

        if module.params.get('action') == "create":
            # Changed is always set to true when provisioning new AMI
            if not module.params.get('instance_id'):
                module.fail_json(msg='instance_id is required for new image')

        if module.params.get('action') == "register":
            if not module.params.get('virtualization_type'):
                module.fail_json(
                    msg='virtualization_type is required for new image')

            if module.params.get('virtualization_type') not in ['paravirtual', 'hvm']:
                module.fail_json(msg='virtualization_type must be either paravirtual or hvm')

            if not module.params.get('snapshot_id') and \
               not module.params.get('device_mapping'):
                module.fail_json(msg='either snapshot_id or device_mapping '
                                     'is required for new image')

            if module.params.get('snapshot_id') and \
               module.params.get('device_mapping'):
                module.fail_json(msg='device_mapping is mutually '
                                     'exclusive with snapshot_id')

            if module.params.get('architecture') not in ['x86_64', 'i386']:
                module.fail_json(msg='architecture must be eith x86_64 or i386')

            if module.params.get('delete_root_volume_on_termination') and not \
               module.params.get('snapshot_id'):
                module.fail_json(msg='snapshot_id is required when using delete_root_volume_on_termination')

            if module.params.get('sriov_net_support') and \
               module.params.get('sriov_net_support') not in [None, 'simple']:
                module.fail_json(msg='sriov_net_support must be simple or not set')

        if not module.params.get('name'):
            module.fail_json(msg='name parameter is required for new image')
        create_image(module, ec2)



# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
