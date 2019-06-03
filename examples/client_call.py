# coding=utf-8

from __future__ import print_function

import time
import logging
import apyllo


def main():
    apyllo.set_logger(
        'apyllo',
        logging.DEBUG,
        rotate_file_path='/tmp/apyllo.log',
    )
    client = apyllo.client(
        config_server_host="your-apollo-meta-service.com",
        fallback_to_local=False,
        app_id="apyllo-demo",
        namespaces=["application", "demo.yml"],
    )

    # will blocking for seconds while do first-time polling.
    client.start()

    # do your work.
    # e.g. user could manually download ns config.
    # client.download("demo.yml")

    print(
        "got application key `demo` value: {}".format(
            client.get_value("demo", "application", "NONE")
        )
    )

    print(
        "got demo.yml content: \r\n{}".format(
            client.get_content("demo.yml")
        )
    )

    client.stop()


if __name__ == "__main__":
    main()
