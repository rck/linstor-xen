#!/usr/bin/env python

import linstor
import urlparse
import os
import sys
import xapi
import xapi.storage.api.v5.datapath
import xapi.storage.api.v5.volume
from xapi.storage import log

from xapi.storage.linstor.common import SCHEME


class Implementation(xapi.storage.api.v5.datapath.Datapath_skeleton):

    @classmethod
    def _parse(cls, uri):
        # parses the uri and does executes checks (e.g., scheme)
        if not uri.startswith(SCHEME):
            pass  # TODO(rck)

        # we have to parse it as http, otherwise parameters are parsed wrong
        return urlparse.urlparse('http'+uri[len(SCHEME):])

    @classmethod
    def _get_controller(cls, uri):
        controller = 'localhost'
        u = cls._parse(uri)
        for p in u.params.split(';'):
            if p.startswith('controller='):
                controller = p.split('=')[1]
                break

        # TODO(rck)
        # raise xapi.storage.api.v5.volume.Volume_does_not_exist(u.path)
        return '{}://{}'.format(SCHEME, controller)

    @classmethod
    def _get_node(cls, uri):
        node = cls._parse(uri).netloc
        if not node:
            pass
        # TODO(rck)
            # raise xapi.storage.api.v5.volume.Volume_does_not_exist(u.path)
        return node

    @classmethod
    def _get_res(cls, uri):
        res = cls._parse(uri).path
        if not res or len(res) == 0:
            pass
        # TODO(rck)
            # raise xapi.storage.api.v5.volume.Volume_does_not_exist(u.path)

        # path contains the leading '/'
        return res[1:]

    def open(self, dbg, uri, persistent):
        node_name = self._get_node(uri)
        res_name = self._get_res(uri)
        controller = self._get_controller(uri)

        res = linstor.Resource(res_name, controller)
        # in linstor we call that step activate, that is fine, see comment in self.activate()
        res.activate(node_name)

        # raise xapi.storage.api.v5.volume.Volume_does_not_exist(u.path)
        return None

    def attach(self, dbg, uri, domain):
        res_name = self._get_res(uri)
        controller = self._get_controller(uri)

        res = linstor.Resource(res_name, controller)
        return {
            'implementations': [['BlockDevice', {'path': res.volumes[0].device_path}]],
        }

    def activate(self, dbg, uri, domain):
        # that would be the part where we would switch to DRBD Primary
        # not necessary with DRBD9, as it has auto-promote
        pass

    def deactivate(self, dbg, uri, domain):
        # intentional; nothing to do
        pass

    def detach(self, dbg, uri, domain):
        # intentional; nothing to do
        pass

    def close(self, dbg, uri):
        node_name = self._get_node(uri)
        res_name = self._get_res(uri)
        controller = self._get_controller(uri)

        res = linstor.Resource(res_name, controller)
        res.deactivate(node_name)
        return None


if __name__ == "__main__":
    log.log_call_argv()
    cmd = xapi.storage.api.v5.datapath.Datapath_commandline(Implementation())
    base = os.path.basename(sys.argv[0])
    if base == "Datapath.activate":
        cmd.activate()
    elif base == "Datapath.attach":
        cmd.attach()
    elif base == "Datapath.close":
        cmd.close()
    elif base == "Datapath.deactivate":
        cmd.deactivate()
    elif base == "Datapath.detach":
        cmd.detach()
    elif base == "Datapath.open":
        cmd.open()
    else:
        raise xapi.storage.api.v5.datapath.Unimplemented(base)
