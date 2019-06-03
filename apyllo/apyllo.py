# coding=utf-8

'''
1. init client
2. start and try load from local, sync and update cache
3. entering long polling and maintains local cache dump
4. exit
'''

import os
import shutil
import logging
import json
import requests
from .requester import WebClient
from .cache import Cache
from .poller import Poller
from .exceptions import InvalidResponseError, NotImplementError
from .constance import *


logger = logging.getLogger(__name__)


class ApolloPollerMixin(Poller):
    def init(self, polling_interval, polling_timeout):
        logger.debug("apollo poller init with interval {}, timeout {}".format(
            polling_interval, polling_timeout
        ))
        super(ApolloPollerMixin, self).init(
            polling_interval=polling_interval,
            polling_timeout=polling_timeout
        )

    def _do_polling(self):
        '''
        override of `_do_polling`, check notifications and popout events.
        '''
        updates = self._polling_notificatios()
        if not updates:
            return

        for update in updates:
            ns = update['namespaceName']
            nid = update['notificationId']
            logger.debug(
                "got notification change on {} with notification id {}".format(
                    ns, nid
                )
            )
            self._sync(ns)
            self._update_notification(ns, nid)
            self._dump(namespace=ns)
            yield update
        return

    def _preload(self):
        logger.debug("do first time preload")
        self._pre_load_from_local()
        for event in self._do_polling():
            pass
        logger.debug("first time preload done")

    def start(self):
        self._preload()
        super(ApolloPollerMixin, self).start()

    def stop(self):
        super(ApolloPollerMixin, self).stop()


class Apyllo(WebClient, ApolloPollerMixin):
    '''
    In python, as GIL exists, thus dict is thread-safe,
    see: https://docs.python.org/3/glossary.html#term-global-interpreter-lock
    BTW, as we said, apyllo ONLY supports Cython due to using GIL.
    '''
    def __init__(
        self, config_server_host, app_id, cluster=DEFAULT_CLUSTER,
        namespaces=DEFAULT_NAMESPACES,
        ip=None,
        fallback_to_local=DEFAULT_FALLBACK_TO_LOCAL,
        cache_dir=DEFAULT_CACHE_DIR,
        cache_file_name_fmt=DEFAULT_CACHE_FILE_NAME_FMT,
        query_timeout=DEFAULT_QUERY_TIMEOUT,
        polling_interval=DEFAULT_POLLING_INTERVAL,
        polling_timeout=DEFAULT_POLLING_TIMEOUT, **kwargs
    ):
        self.config_server_host = config_server_host
        self.app_id = app_id
        self.cluster = cluster

        # NOTE: NEED TO BE thread-safe
        self.namespaces = namespaces

        self.ip = self._init_ip(ip)
        self.query_timeout = query_timeout

        # whether fallback to local cached files while server is unavailable
        self.fallback_to_local = fallback_to_local

        # set poller
        self.init(
            polling_interval=polling_interval,
            polling_timeout=polling_timeout
        )

        self.cache_dir = cache_dir
        self.cache_file_name_fmt = cache_file_name_fmt

        # whole config cache with namespace as the key
        self._cache = Cache(name="{}.{}".format(
            self.app_id, self.cluster)
        )

        # FIXME: support releaseKey on load local
        self._release_key_cache = Cache(
            name=DEFAULT_RELEASE_KEY_CACHE_NAME,
            data=dict(map(
                lambda ns: (ns, DEFAULT_RELEASE_KEY),
                namespaces
            ))
        )

        self._notifications = Cache(
            name=DEFAULT_NOTIFICATION_CACHE_NAME,
            data=dict(map(
                lambda ns: (ns, DEFAULT_NOTIFICATION_ID),
                namespaces
            ))
        )

        # default request timeout set with `query_timeout`
        super(Apyllo, self).__init__(
            host=config_server_host, timeout=query_timeout, **kwargs
        )

    def _init_ip(self, ip):
        if ip:
            self.ip = ip
        else:
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((DEFAULT_IP_PROBE_DNS_SERVER, 53))
                ip = s.getsockname()[0]
            finally:
                s.close()
            self.ip = ip

    def _get_nocache_configs(
        self, namespace=DEFAULT_NAMESPACE, release_key=DEFAULT_RELEASE_KEY
    ):
        path = "/configs/{}/{}/{}".format(
            self.app_id, self.cluster,
            namespace,
        )
        params = {
            "ip": self.ip,
            "releaseKey": release_key
        }
        ret = self._do_request("GET", path, params)
        if ret.status_code == 304:
            # no update
            logger.debug("namespace {} no change with release key {}".format(
                namespace, release_key
            ))
            return None
        else:
            return ret.json()

    def _get_cached_configs(self, namespace=DEFAULT_NAMESPACE):
        path = "/configfiles/json/{}/{}/{}".format(
            self.app_id, self.cluster, namespace,
        )
        params = {
            "ip": self.ip,
        }
        ret = self._do_request("GET", path, params)
        return ret.json()

    def _polling_notificatios(self):
        path = "/notifications/v2"
        notifications = []
        for key in self._notifications.keys():
            notifications.append({
                "namespaceName": key,
                "notificationId": self._notifications[key],
            })
        params = {
            "appId": self.app_id,
            "cluster": self.cluster,
            "notifications": json.dumps(notifications, ensure_ascii=False)
        }

        logger.debug("polling notifications with params {}".format(
            json.dumps(params)
        ))

        try:
            ret = self._do_request(
                "GET", path, params, timeout=self.polling_timeout
            )
        except requests.exceptions.Timeout:
            logger.debug("notification watch timeout")
            return []
        except requests.exceptions.RequestException as e:
            logger.error("polling notifications with error: {}".format(str(e)))
            if self.fallback_to_local is True:
                return []
            else:
                raise e

        if ret.status_code == 304:
            logger.debug("no change detect from notification watch")
            return []

        if ret.status_code == 200:
            updates = ret.json()
            return updates

        raise InvalidResponseError(self.config_server_host, ret.text)

    def _pre_load_from_local(self):
        logger.debug("try load config from local files")
        for ns in self.namespaces:
            path = self._get_path(ns)
            if not os.path.exists(path):
                continue

            data = None
            with open(path, "r") as fp:
                data = fp.read()
            if not data:
                continue

            cache_data = json.loads(data)
            if not isinstance(cache_data, dict):
                continue

            release_key = cache_data["releaseKey"]
            self._update_cache(ns, cache_data)
            self._update_release_key(ns, release_key)
            logger.debug(
                "loaded config for ns {}, local path {} with release_key {}"
                .format(
                    ns, path, release_key
                )
            )

    def _update_notification(self, namespace, notification_id):
        self._notifications.set(namespace, notification_id)

    def _update_release_key(self, namespace, release_key):
        self._release_key_cache.set(namespace, release_key)

    def _update_cache(self, namespace, configs):
        self._cache.set(namespace, configs)

    def _sync(self, namespace=DEFAULT_NAMESPACE):
        release_key = self._release_key_cache[namespace]
        data = self._get_nocache_configs(namespace, release_key)
        if isinstance(data, dict):
            # sync cache and release key
            configs = data
            new_release_key = data["releaseKey"]
            self._update_cache(namespace, configs)
            self._update_release_key(namespace, new_release_key)
            logger.debug(
                "cache config updated for ns {}, new release_key {}"
                .format(
                    namespace, new_release_key
                )
            )
            return True
        else:
            logger.debug(
                "cache config no update for ns {} release_key {}"
                .format(
                    namespace, release_key
                )
            )
            return False

    def _get_path(self, namespace=DEFAULT_NAMESPACE):
        cache_dir = self.cache_dir
        file_name = self.cache_file_name_fmt.format(
            app_id=self.app_id, cluster=self.cluster, namespace=namespace
        )
        path = os.path.join(cache_dir, file_name)
        return path

    def _get_rotate_path(
        self, namespace=DEFAULT_NAMESPACE,
        rotate_suffix=DEFAULT_DUMP_ROTATE_SUFFIX
    ):
        path = self._get_path(namespace)
        rotate_path = "{}{}".format(path, rotate_suffix)
        return rotate_path

    def _get_ns_suffix(self, namespace):
        suffix = namespace.split(".")[-1]
        return suffix

    def _dump(
        self, namespace=DEFAULT_NAMESPACE
    ):
        path = self._get_path(namespace)
        rotate_path = self._get_rotate_path(namespace)
        with open(rotate_path, "w") as fp:
            data = self._cache[namespace]
            fp.write(json.dumps(data))
        shutil.move(rotate_path, path)
        logger.debug("cache {} for ns {} dumped".format(path, namespace))

    def download(
        self, namespace,
        download_dir=DEFAULT_DUMP_DIR,
        download_file_name_fmt=DEFAULT_DUMP_FILE_NAME_FMT
    ):
        self._sync(namespace)

        data = self._cache[namespace]
        path = os.path.join(download_dir, download_file_name_fmt.format(
            app_id=self.app_id, cluster=self.cluster, namespace=namespace
        ))
        with open(path, "w") as fp:
            ns_suffix = self._get_ns_suffix(namespace)
            if ns_suffix in ("yaml", "yml"):
                yaml_content = data["configurations"]["content"]
                fp.write(yaml_content)
            else:
                json_content = data["configurations"]
                fp.write(json.dumps(json_content))
        logger.debug("ns {} downloaded into {}".format(namespace, path))

    def subscribe_namespace(self, namespace):
        # TODO: support subscribe namespace at runtime.
        raise NotImplementError("subscribe more namespace")

    def get_content(self, namespace=DEFAULT_NAMESPACE):
        suffix = self._get_ns_suffix(namespace)
        data = self._cache[namespace]["configurations"]["content"]
        return data

    def get_value(self, key, namespace=DEFAULT_NAMESPACE, default_value=None):
        return self._cache[namespace]["configurations"].get(key, default_value)
