#!/usr/bin/env python

import os
import os.path
import sys
import xapi.storage.api.v5.volume
from xapi.storage import log

from xapi.storage.linstor.common import SRHelper


class Implementation(xapi.storage.api.v5.volume.SR_skeleton):

    def probe(self, dbg, configuration):
        raise AssertionError("not implemented")

    def attach(self, dbg, configuration):
        return 'linstor+kv:///' + configuration['key']

    def create(self, dbg, uuid, configuration, name, description):
        configuration['key'] = str(uuid)
        configuration['name'] = name
        configuration['description'] = description

        SRHelper.write_stat(configuration)
        return configuration

    def destroy(self, dbg, sr):
        SRHelper.delete_stat(sr)

    def detach(self, dbg, sr):
        # assume there is no need to unmount the filesystem
        return

    def ls(self, dbg, sr):
        stat = SRHelper.read_stat(sr)
        if not stat:
            raise xapi.storage.api.v5.volume.Sr_not_attached(sr)
        # xen does not allow values != string in the configuration, so store volumes "," separated
        return SRHelper.get_volumes(sr)

    def stat(self, dbg, sr):
        # TODO(rck): obviously fake
        physical_size = 1*1024*1024*1024*1024
        free_size = physical_size/2

        ret = {
            "sr": sr,
            "name": "UNKNOWN",
            "description": "UNKNOWN",
            "total_space": physical_size,
            "free_space": free_size,
            "datasources": [],
            "clustered": False,
            "health": ["Healthy", ""]
        }
        stat = SRHelper.read_stat(sr)

        if not stat:
            return ret

        try:
            ret['name'] = stat['name']
        except KeyError:
            pass

        try:
            ret['description'] = stat['description']
        except KeyError:
            pass

        return ret


if __name__ == "__main__":
    log.log_call_argv()
    cmd = xapi.storage.api.v5.volume.SR_commandline(Implementation())
    base = os.path.basename(sys.argv[0])
    if base == 'SR.probe':
        cmd.probe()
    elif base == 'SR.attach':
        cmd.attach()
    elif base == 'SR.create':
        cmd.create()
    elif base == 'SR.destroy':
        cmd.destroy()
    elif base == 'SR.detach':
        cmd.detach()
    elif base == 'SR.ls':
        cmd.ls()
    elif base == 'SR.stat':
        cmd.stat()
    else:
        raise xapi.storage.api.v5.volume.Unimplemented(base)
