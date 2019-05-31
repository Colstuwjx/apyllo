# coding=utf-8

import time
import logging
import gevent
from gevent import monkey


monkey.patch_all()


logger = logging.getLogger(__name__)


class Poller(object):
    def init(self, polling_interval, polling_timeout):
        self.polling_interval = polling_interval
        self.polling_timeout = polling_timeout

    def start(self):
        self.stopped = False
        gevent.spawn(self._polling)
        logger.debug("long polling started")

    def stop(self):
        logger.debug("long polling stopped")
        self.stopped = True

    def _do_polling(self):
        # here we can popout events, rather than return empty array.
        logger.debug("polling with timeout {}".format(self.polling_timeout))
        return []

    def _polling(self):
        while not self.stopped:
            # TODO: send events if get changes
            self._do_polling()
            time.sleep(self.polling_interval)


# if __name__ == "__main__":
#     poller = Poller()
#     poller.init(3, 90)
#     poller.start()

#     while True:
#         time.sleep(5)
