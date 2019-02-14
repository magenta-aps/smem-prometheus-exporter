# Shared Memory Prometheus Exporter
[Prometheus](https://prometheus.io/) exporter for shared shared memory metrics via [smem](https://www.selenic.com/smem/).
Shared memory details are picked up from the `/proc` filesystem and processed.

Similar to the `mongodb_exporter` and `node_exporter` this exporter has been implemented as a standalone-service to make reuse easier across different platforms and hosts.

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
Upon which a full smem default run will be printed, followed by:
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
smem_user{reading_type="count",user="user",user_id="1000"} 62.0
smem_user{reading_type="pss",user="user",user_id="1000"} 2.475652e+06
...
# HELP smem_system Memory usage for the system
# TYPE smem_system gauge
smem_system{area="free memory",reading_type="noncache"} 0.0
smem_system{area="kernel image",reading_type="noncache"} 0.0
...
# HELP smem_pid Memory usage by process
# TYPE smem_pid gauge
smem_pid{command="/usr/bin/dbus-daemon ...",pid="7888",reading_type="pss",user="user",user_id="1000"} 459.0
smem_pid{command="/usr/bin/python ...",pid="8610",reading_type="maps",user="user",user_id="1000"} 1245.0
...
```
Along with the default entries for `python` and `process`.

The following metrics are provided:
* `smem_map` exposes memory maps and shared memory regions, labeled by path and reading type.
* `smem_user` exposes memory usage for users, labeled by user, user_id and reading type.
* `smem_system` exposes memory areas for the system, labeled by area and reading_type.
* `smem_pid` exposes memory usage for processes, labeled by command, pid, user, user_id and reading_type.

## Limitations
While running as non-root smem can only query so much information from `/proc/`.
As such this exporter can only export so much information when running as non-root.

To work around this, either:
* Run the exporter as root (bad solution), or
* mount `/proc` with the gid option and add the export user to the corresponding group.

## Future considerations
Below follows a list of ideas for future improvements:
* Adapt to [futurization-smem](https://github.com/necromuralist/smem)?
* Support commandline flags via argparse?
    * Support for enabling / disabling entire exporters (map, user, system, pid).
    * Support for enabling / disabling based upon labels.
    * Support truncating long commands with ellipsis.
    * Support transforming long commands into just the executable name.
      - Alternatively adding a new label just for executable name might do.
* Utilize [Custom Collectors](https://github.com/prometheus/client_python#custom-collectors) instead of Gauge + resetting.
    
