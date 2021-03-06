# coding=utf-8

# defaults
DEFAULT_FALLBACK_TO_LOCAL = False
DEFAULT_NAMESPACE = "application"
DEFAULT_NAMESPACES = [DEFAULT_NAMESPACE]
DEFAULT_CLUSTER = "default"
DEFAULT_QUERY_TIMEOUT = 2
DEFAULT_POLLING_INTERVAL = 3
DEFAULT_POLLING_TIMEOUT = 90
DEFAULT_IP_PROBE_DNS_SERVER = "8.8.8.8"
DEFAULT_RELEASE_KEY_CACHE_NAME = "releaseKey"
DEFAULT_RELEASE_KEY = -1
DEFAULT_NOTIFICATION_ID = -1
DEFAULT_NOTIFICATION_CACHE_NAME = "notification"
DEFAULT_CACHE_DIR = "/tmp"
DEFAULT_CACHE_FILE_NAME_FMT = ".{app_id}_{cluster}_{namespace}"
DEFAULT_DUMP_DIR = "."
DEFAULT_DUMP_ROTATE_SUFFIX = ".tmp"
DEFAULT_DUMP_FILE_NAME_FMT = "{app_id}_{cluster}_{namespace}"
DEFAULT_ROTATE_FILE_PATH = "/data/logs/apyllo/apyllo.log"
DEFAULT_ROTATE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_ROTATE_COUNT = 5
