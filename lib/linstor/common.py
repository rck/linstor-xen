import collections
import json
import linstor
import urlparse
import os.path

XENKV = 'xen-plugin-linstor'
XENNS = '/xen/'
SRNS = os.path.join(XENNS, 'sr')

VOLS_KEY = 'volumes'
SCHEME = 'linstor'

LinstorXENConfig = collections.namedtuple('LinstorXENConfig', ['controller', 'redundancy'])
LINSTOR_CONFIG = '/etc/linstor/linstor-client.conf'


class ConfigHelper(object):
    @classmethod
    def _get_config(cls, config_file=LINSTOR_CONFIG):
        try:
            import ConfigParser as configparser
        except ImportError:
            import configparser

        cp = configparser.SafeConfigParser()

        controller, redundancy = SCHEME + '://localhost', 2
        try:
            cp.read(config_file)
        except Exception:
            return LinstorXENConfig(controller, redundancy)

        try:
            controllers = cp.get('global', 'controllers')
            controller = controllers.split(',')[0]
        except Exception:
            pass

        try:
            redundancy = int(cp.get('xen', 'redundancy'))
        except Exception:
            pass

        return LinstorXENConfig(controller, redundancy)


class SRHelper(object):
    @classmethod
    def write_stat(cls, meta, namespace=SRNS):
        key = meta['key']
        cfg = ConfigHelper._get_config()
        kv = linstor.KV(XENKV, namespace=namespace, uri=cfg.controller)
        kv[key] = json.dumps(meta)

    @classmethod
    def read_stat(cls, sr):
        key = urlparse.urlparse(sr).path[1:]
        cfg = ConfigHelper._get_config()
        kv = linstor.KV(XENKV, namespace=SRNS, uri=cfg.controller)
        stat = {}
        try:
            stat = json.loads(kv[key])
        except KeyError:
            pass
        return stat

    @classmethod
    def add_volume(cls, sr, vol_meta):
        sr_key = urlparse.urlparse(sr).path[1:]
        cls.write_stat(vol_meta, namespace=os.path.join(SRNS, sr_key))

    @classmethod
    def delete_volume(cls, sr, vol_meta):
        vol_key = vol_meta['key']
        sr_key = urlparse.urlparse(sr).path[1:]
        cfg = ConfigHelper._get_config()
        kv = linstor.KV(XENKV, namespace=os.path.join(SRNS, sr_key), uri=cfg.controller)
        del(kv[vol_key])

    @classmethod
    def get_volume(cls, sr, vol_key):
        cfg = ConfigHelper._get_config()
        sr_key = urlparse.urlparse(sr).path[1:]
        kv = linstor.KV(XENKV, namespace=os.path.join(SRNS, sr_key), uri=cfg.controller)
        return json.loads(kv[vol_key])

    @classmethod
    def get_volumes(cls, sr):
        cfg = ConfigHelper._get_config()
        sr_key = urlparse.urlparse(sr).path[1:]
        kv = linstor.KV(XENKV, namespace=os.path.join(SRNS, sr_key), uri=cfg.controller)
        return [json.dumps(v) for v in kv.values()]

    @classmethod
    def delete_stat(cls, sr, namespace=SRNS):
        key = urlparse.urlparse(sr).path[1:]
        cfg = ConfigHelper._get_config()
        kv = linstor.KV(XENKV, namespace=namespace, uri=cfg.controller)
        try:
            del(kv[key])
        except KeyError:
            # assume it is already gone
            pass

    @classmethod
    def set_kv(cls, sr, vol_key, k, v):
        stat = cls.get_volume(sr, vol_key)
        stat['keys'][k] = v
        cls.add_volume(sr, stat)

    @classmethod
    def unset_kv(cls, sr, vol_key, k):
        stat = cls.get_volume(sr, vol_key)
        del(stat['keys'][k])
        cls.add_volume(sr, stat)

    @classmethod
    def _set_volume(cls, sr, vol_key, k, v):
        stat = cls.get_volume(sr, vol_key)
        stat[k] = v
        cls.add_volume(sr, stat)

    @classmethod
    def set_name(cls, sr, vol_key, name):
        cls._set_volume(sr, vol_key, 'name', name)

    @classmethod
    def set_description(cls, sr, vol_key, description):
        cls._set_volume(sr, vol_key, 'description', description)
