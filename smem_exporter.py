from prometheus_client import Gauge

def export(guage, keys, fields, label_fields, read_fields):
    guage._metrics.clear()
    for n in keys:
        labels = {}
        for c in label_fields:
            value = str(fields[c](n))
            labels[c] = ''.join([i if ord(i) < 128 else ' ' for i in value])
        for c in read_fields:
            labels['reading_type'] = c
            value = fields[c](n)
            guage.labels(**labels).set(value)


from smem import processtotals, pidusername, src
memory_usage_pid = Gauge('smem_pid', 'Memory usage by process', ['pid', 'user_id', 'user', 'command', 'reading_type'])
def export_pids():
    # Read pids and process memory
    p = src.pids()
    pt = processtotals(p)

    fields = dict(
        pid=lambda n: n,
        user=pidusername,
        user_id=src.piduser,
        name=src.pidname,
        command=src.pidcmd,
        maps=lambda n: pt[n]['maps'],
        swap=lambda n: pt[n]['swap'],
        uss=lambda n: pt[n]['uss'],
        rss=lambda n: pt[n]['rss'],
        pss=lambda n: pt[n]['pss'],
        vss=lambda n: pt[n]['size'],
    )

    export(
        memory_usage_pid,
        pt.keys(),
        fields,
        ['pid', 'user_id', 'user', 'command'],
        ['maps', 'swap', 'uss', 'rss', 'pss', 'vss'],
    )


from smem import usertotals
memory_usage_user = Gauge('smem_user', 'Memory usage by user', ['user_id', 'user', 'reading_type'])
def export_users():
    # Read pids and user memory
    p = src.pids()
    pt = usertotals(p)

    fields = dict(
        user_id=lambda n: n,
        user=src.username,
        count=lambda n: pt[n]['count'],
        swap=lambda n: pt[n]['swap'],
        uss=lambda n: pt[n]['private_clean'] + pt[n]['private_dirty'],
        rss=lambda n: pt[n]['rss'],
        pss=lambda n: pt[n]['pss'],
        vss=lambda n: pt[n]['size'],
    )

    export(
        memory_usage_user,
        pt.keys(),
        fields,
        ['user_id', 'user'],
        ['count', 'swap', 'uss', 'rss', 'pss', 'vss'],
    )


from smem import maptotals
memory_usage_map = Gauge('smem_map', 'Memory usage maps', ['map', 'reading_type'])
def export_maps():
    p = src.pids()
    pt = maptotals(p)

    fields = dict(
        map=lambda n: n,
        count=lambda n: pt[n]['count'],
        pids=lambda n: pt[n]['pids'],
        swap=lambda n: pt[n]['swap'],
        uss=lambda n: pt[n]['private_clean'] + pt[n]['private_dirty'],
        rss=lambda n: pt[n]['rss'],
        pss=lambda n: pt[n]['pss'],
        vss=lambda n: pt[n]['size'],
        avgpss=lambda n: int(1.0 * pt[n]['pss']/pt[n]['pids']),
        avguss=lambda n: int(1.0 * (pt[n]['private_clean'] + pt[n]['private_dirty'])/pt[n]['pids']),
        avgrss=lambda n: int(1.0 * pt[n]['rss']/pt[n]['pids']),
    )

    export(
        memory_usage_map,
        pt.keys(),
        fields,
        ['map'],
        ['count', 'pids', 'swap', 'uss', 'rss', 'pss', 'vss', 'avgpss', 'avguss', 'avgrss'],
    )


from smem import totalmem, kernelsize, memory
memory_usage_system = Gauge('smem_system', 'Memory usage for the system', ['area', 'reading_type'])
def export_system():
    t = totalmem()
    ki = kernelsize()
    m = memory()

    mt = m['memtotal']
    f = m['memfree']

    # total amount used by hardware
    fh = max(t - mt - ki, 0)

    # total amount mapped into userspace (ie mapped an unmapped pages)
    u = m['anonpages'] + m['mapped']

    # total amount allocated by kernel not for userspace
    kd = mt - f - u

    # total amount in kernel caches
    kdc = m['buffers'] + m['sreclaimable'] + (m['cached'] - m['mapped'])

    l = [
        ("firmware/hardware", fh, 0),
        ("kernel image", ki, 0),
        ("kernel dynamic memory", kd, kdc),
        ("userspace memory", u, m['mapped']),
        ("free memory", f, f)
    ]

    fields = dict(
        area=lambda n: l[n][0],
        used=lambda n: l[n][1],
        cache=lambda n: l[n][2],
        noncache=lambda n: l[n][1] - l[n][2],
    )

    export(
        memory_usage_system,
        range(len(l)),
        fields,
        ['area'],
        ['used', 'cache', 'noncache']
    )

def update_readings():
    # print "Updating readings..."
    export_pids()
    export_users()
    export_maps()
    export_system()
    # print "OK"

from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server
import time

# TODO: Configurable options, including port
update_interval = 10

app = make_wsgi_app()
httpd = make_server('0.0.0.0', 8172, app)
print "Starting HTTPD on 0.0.0.0:8172"
last = time.time()
update_readings()
while True:
    # Timeout handle_requests every second, to check whether we need to update
    # our readings.
    httpd.timeout = 1
    httpd.handle_request()
    now = time.time()
    # Only update every 'update_interval' seconds
    if now - last > update_interval:
        update_readings()
        last = time.time()
