# smem prometheus exporter
[Prometheus](https://prometheus.io/) exporter for shared shared memory metrics via [smem](https://www.selenic.com/smem/).

## Building
```
wget https://www.selenic.com/smem/download/smem-1.4.tar.gz
tar -xzvf smem-1.4.tar.gz
mv smem-1.4 smem
mv smem/smem smem/smem.py
echo "from smem import *" > smem/__init__.py
```
This downloads the latest release of smem, and configures it to be used as a python library.

## Running
```
python smem_exporter.py
```
Upon which a lot will be printed, ending with:
```
Starting HTTPD on 0.0.0.0:8172
```
After which the metrics endpoint is available at:
* http://localhost:8172/metrics

## Output
Navigating to the metrics url, should produce output alike the following:
```
# HELP smem_map Memory usage maps
# TYPE smem_map gauge
smem_map{map="/usr/lib/x86_64-linux-gnu/libxcb-render.so.0.0.0",reading_type="uss"} 100.0
smem_map{map="/usr/share/fonts/type1/gsfonts/n019063l.pfb",reading_type="vss"} 612.0
...
# HELP smem_user Memory usage by user
# TYPE smem_user gauge
smem_user{reading_type="count",user="username",user_id="1000"} 62.0
smem_user{reading_type="pss",user="username",user_id="1000"} 2.475652e+06
...
# HELP smem_system Memory usage for the system
# TYPE smem_system gauge
smem_system{area="free memory",reading_type="noncache"} 0.0
smem_system{area="kernel image",reading_type="noncache"} 0.0
...
# HELP smem_pid Memory usage by process
# TYPE smem_pid gauge
smem_pid{command="/usr/bin/dbus-daemon ...",pid="7888",reading_type="pss",user="username",user_id="1000"} 459.0
smem_pid{command="/usr/bin/python /usr/share/virt-manager/virt-manager",pid="8610",reading_type="maps",user="username",user_id="1000"} 1245.0
...
```
Along with the default entries for `python` and `process`.

## Limitations
While running as non-root smem can only query so much information from `/proc/`.
As such this exporter can only export so much information when running as non-root.

To work around this, either:
* Run the exporter as root (bad solution), or
* mount `/proc` with the gid option and add the export user to the corresponding group.

## Future considerations
Adapt to [futurization-smem](https://github.com/necromuralist/smem)?
Support commandline flags via argparse?
