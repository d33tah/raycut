import atexit

import urllib.request
import subprocess

import raycut

cluster_config = raycut.new_cluster_config()
cluster_config["available_node_types"]["ray.head.default"]["node_config"][
    "InstanceType"
] = "c6gd.metal"
cluster_config["available_node_types"]["ray.head.default"]["node_config"][
    "ImageId"
] = "ami-014a542cf4d33b681"
cluster_config['initialization_commands'] += [
    'sudo apt-get update && sudo apt-get install docker.io -y',
    'sudo usermod -aG docker $USER',
    'lsblk',
    '[ -f /dev/md0 0 ] || ( '
    ' sudo mdadm --create --level 0 --raid-devices 2 /dev/md0 /dev/nvme{1,2}n1'
    ' && sudo mkfs.ext4 -F /dev/md0 '
    ' && sudo mount /dev/md0 /mnt '
    ' && sudo chown 1000:1000 /mnt -v )',
]
cluster_config['docker']['run_options'] = ['-v', '/mnt:/mnt']
cluster_config['docker']['image'] = 'rayproject/ray:nightly-py38-cpu-aarch64'
# cluster_config['provider']['cache_stopped_nodes'] = False
ray = raycut.init(cluster_config=cluster_config)
atexit.register(ray.teardown)


@raycut.ray.remote
def get_aws_ip():
    url = "http://169.254.169.254/latest/meta-data/public-ipv4"
    ret = urllib.request.urlopen(url).read().decode("utf-8")
    df = subprocess.check_output(["df", "-h"]).decode("utf-8")
    return ret + "\n" + df

print(ray.run(get_aws_ip)[0])
