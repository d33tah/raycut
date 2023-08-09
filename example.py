import urllib.request
import raycut
import atexit

ray = raycut.init()
atexit.register(ray.teardown)


@raycut.ray.remote
def get_aws_ip():
    url = 'http://169.254.169.254/latest/meta-data/public-ipv4'
    return urllib.request.urlopen(url).read().decode('utf-8')


print(ray.run(get_aws_ip))
