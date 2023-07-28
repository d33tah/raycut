import subprocess
import pathlib
import time

import ray

yaml = '''
cluster_name: default
max_workers: 2
upscaling_speed: 1.0
docker:
    image: "rayproject/ray-ml:latest-cpu"
    container_name: "ray_container"
    pull_before_run: True
    run_options:
        - --ulimit nofile=65536:65536
idle_timeout_minutes: 5
provider:
    type: aws
    region: us-west-2
    availability_zone: us-west-2a,us-west-2b
auth:
    ssh_user: ubuntu
available_node_types:
    ray.head.default:
        resources: {}
        node_config:
            InstanceType: m5.large
            ImageId: ami-0d88d9cbe28fac870
            BlockDeviceMappings:
                - DeviceName: /dev/sda1
                  Ebs:
                      VolumeSize: 140
                      VolumeType: gp3
    ray.worker.default:
        min_workers: 1
        max_workers: 2
        resources: {}
        node_config:
            InstanceType: m5.large
            ImageId: ami-0387d929287ab193e
head_node_type: ray.head.default
file_mounts: {
}
cluster_synced_files: []
file_mounts_sync_continuously: False
initialization_commands: []
setup_commands: []
head_setup_commands: []
worker_setup_commands: []
head_start_ray_commands:
    - ray stop
    - ray start --head --port=6379 --object-manager-port=8076 --autoscaling-config=~/ray_bootstrap_config.yaml --dashboard-host=0.0.0.0
worker_start_ray_commands:
    - ray stop
    - ray start --address=$RAY_HEAD_IP:6379 --object-manager-port=8076
'''


def init(aws_access_key_id, aws_secret_access_key):
    subprocess.check_call(
        'mkdir -p ~/.aws', shell=True)
    subprocess.check_call('pip install boto3 ray', shell=True)
    subprocess.check_call('apt update && apt install rsync -y', shell=True)

    p = pathlib.Path('~/.aws/').expanduser()
    try:
        (p / 'credentials').rename(p / f'credentials_backup_{time.time()}')
    except FileNotFoundError:
        pass
    with open(p / 'credentials', 'w') as f:
        f.write(f'''
        # added by raycut
        [default]
        aws_access_key_id = {aws_access_key_id}
        aws_secret_access_key = {aws_secret_access_key}
        ''')

    with open('example.yaml', 'w') as f:
        f.write(yaml)

    subprocess.check_call('ray up example.yaml --yes', shell=True)
    p = subprocess.Popen('ray attach -p 10001 example.yaml', shell=True)
    ray.init(address='ray://localhost:10001')

    class cls:
        def run(self, f):
            return ray.get([f.remote()])

        def teardown(self):
            p.kill()
            p.wait()
            subprocess.check_call('ray down example.yaml --yes', shell=True)

    return cls()
