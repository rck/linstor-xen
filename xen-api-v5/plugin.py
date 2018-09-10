#!/usr/bin/env python

import os
import sys
import xapi
import xapi.storage.api.v5.plugin
from xapi.storage import log


class Implementation(xapi.storage.api.v5.plugin.Plugin_skeleton):

    def diagnostics(self, dbg):
        return "No diagnostics data"

    def ls(self, dbg):
        raise xapi.storage.api.v5.plugin.Unimplemented(base)
        # return ["string"]

    def query(self, dbg):
        return {
            "plugin": "linstor",
            "name": "The LINBIT LINSTOR Plugin",
            "description": ("This plugin integrates DRBD via LINSTOR in XEN"),
            "vendor": "LINBIT",
            "copyright": "(C) 2018-2019 LINBIT",
            "version": "1.0",
            "required_api_version": "5.0",
            "features": [
                "SR_ATTACH",
                "SR_DETACH",
                "SR_CREATE",
                "VDI_CREATE",
                "VDI_DESTROY",
                "VDI_ATTACH",
                "VDI_ATTACH_OFFLINE",
                "VDI_DETACH",
                "VDI_ACTIVATE",
                "VDI_DEACTIVATE",
                "VDI_CLONE",
                "VDI_SNAPSHOT",
                "VDI_RESIZE",
                "SR_METADATA",
            ],
            "configuration": {},
            "required_cluster_stack": []}


if __name__ == "__main__":
    log.log_call_argv()
    cmd = xapi.storage.api.v5.plugin.Plugin_commandline(Implementation())
    base = os.path.basename(sys.argv[0])
    if base == "Plugin.query":
        cmd.query()
    elif base == "Plugin.diagnostics":
        cmd.diagnostics()
    elif base == "Plugin.ls":
        cmd.ls()
    else:
        raise xapi.storage.api.v5.plugin.Unimplemented(base)
