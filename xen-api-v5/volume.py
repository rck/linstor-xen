#!/usr/bin/env python

import linstor
import uuid
import os
import os.path
import socket
import sys
import xapi.storage.api.v5.volume
from xapi.storage import log
import xapi

from xapi.storage.linstor.common import SCHEME
from xapi.storage.linstor.common import SRHelper, ConfigHelper


class Implementation(xapi.storage.api.v5.volume.Volume_skeleton):
    def create(self, dbg, sr, name, description, size, sharable):
        # [djs55/xapi-storage#33]
        size = int(size)  # bytes

        size = max(size, 4 * 1024 * 1024)  # we have am 4M lower limit

        uuid_ = str(uuid.uuid4())
        hostname = socket.gethostname()

        cfg = ConfigHelper._get_config()

        res = linstor.Resource(name, cfg.controller)
        res.volumes[0] = linstor.Volume(size)
        res.placement.redundancy = cfg.redundancy
        res.autoplace()

        controller = cfg.controller[len('linstor://'):]
        stat = {
            "key": name,
            "uuid": uuid_,
            "name": name,
            "sr": sr,
            "description": description,
            "read_write": True,
            "sharable": sharable,
            "virtual_size": size,
            "physical_utilisation": 0,
            "uri": ['{}://{}/{};controller={}'.format(SCHEME, hostname, name, controller)],
            "keys": {},
        }

        SRHelper.add_volume(sr, stat)

        return stat

    def snapshot(self, dbg, sr, key):
        pass

    def clone(self, dbg, sr, key):
        pass

    def destroy(self, dbg, sr, key):
        cfg = ConfigHelper._get_config()

        res = linstor.Resource(key, cfg.controller)
        res.delete()

        meta = {'key': key}
        SRHelper.delete_volume(sr, meta)

    def set_name(self, dbg, sr, key, new_name):
        SRHelper.set_name(sr, key, new_name)

    def set_description(self, dbg, sr, key, new_description):
        SRHelper.set_description(sr, key, new_description)

    def set(self, dbg, sr, key, k, v):
        SRHelper.set_kv(sr, key, k, v)

    def unset(self, dbg, sr, key, k):
        SRHelper.unset_kv(sr, key, k)

    @classmethod
    def _current_size(cls, res_name):
        cfg = ConfigHelper._get_config()
        res = linstor.Resource(res_name, cfg.controller)
        return res.volumes[0].size

    def resize(self, dbg, sr, key, new_size):
        new_size = int(new_size)
        current_size = self._current_size(key)

        if new_size == current_size:
            return
        if new_size < current_size:
            # Raise SMAPIv1 error VDISize
            raise xapi.XenAPIException("SR_BACKEND_FAILURE_79",
                                       ["VDI Invalid size",
                                        "shrinking not allowed"])
        cfg = ConfigHelper._get_config()
        res = linstor.Resource(key, cfg.controller)
        res.volumes[0].size = current_size

    def stat(self, dbg, sr, key):
        cfg = ConfigHelper._get_config()
        current_size = self._current_size(key)
        psize = current_size >> 2  # TODO(rck)
        hostname = socket.gethostname()

        stat = SRHelper.get_volume(sr, key)
        controller = cfg.controller[len('linstor://'):]
        stat['uri'] = ['{}://{}/{};controller={}'.format(SCHEME, hostname, key, controller)]
        stat['virtual_size'] = current_size
        stat['physical_utilisation'] = psize
        return stat


if __name__ == "__main__":
    log.log_call_argv()
    cmd = xapi.storage.api.v5.volume.Volume_commandline(Implementation())
    base = os.path.basename(sys.argv[0])
    if base == "Volume.clone":
        cmd.clone()
    elif base == "Volume.create":
        cmd.create()
    elif base == "Volume.destroy":
        cmd.destroy()
    elif base == "Volume.resize":
        cmd.resize()
    elif base == "Volume.set":
        cmd.set()
    elif base == "Volume.set_description":
        cmd.set_description()
    elif base == "Volume.set_name":
        cmd.set_name()
    elif base == "Volume.snapshot":
        cmd.snapshot()
    elif base == "Volume.stat":
        cmd.stat()
    elif base == "Volume.unset":
        cmd.unset()
    else:
        raise xapi.storage.api.v5.volume.Unimplemented(base)
