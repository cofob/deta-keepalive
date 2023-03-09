from os import environ
from deta import Base, Deta
from time import sleep, time
from random import uniform
from typing import Callable
from secrets import token_urlsafe
from requests import get
from threading import Thread
from requests.exceptions import Timeout


class Pinger:
    def __init__(self, deta: Deta, time_limit: int = 10, kill_hook: Callable = None):
        self.address = f"https://{environ['DETA_PATH']}.deta.dev/"
        self.base: Base = deta.Base("keepalive")
        self.start_time = int(time())
        self.time_limit = time_limit
        self.key = token_urlsafe(8)
        self.spawned: int = 0
        self.kill_hook = kill_hook

    def kill(self):
        # we ourselves end the program, remove the information about us in base
        self.base.delete(self.key)
        if self.kill_hook:
            self.kill_hook()
        exit(1)

    def ping_thread(self):
        if self.spawned < 4:
            get(self.address)
            self.spawned += 1

    def loop_thread(self):
        while True:
            Thread(target=self.ping_thread).start()

            # add a bit of randomness to reduce the chance of collision
            sleep(uniform(0.5, 2))

            # if the life cycle of Micro comes to an end execute kill method
            if self.start_time + self.time_limit - 4 < int(time()):
                self.kill()

            # if there another running Micro's we execute kill method
            if (
                self.base.fetch(
                    {"spawned_at?gte": self.start_time - self.time_limit, "running": True, "key?ne": self.key}
                ).count
                > 0
            ):
                self.kill()

    def run(self):
        # check if we're in Micro
        if environ["DETA_RUNTIME"] != "true":
            return

        # start loop thread
        Thread(target=self.loop_thread).start()

        # publish in about us
        self.base.put({"running": False, "spawned_at": self.start_time}, key=self.key, expire_in=self.time_limit)

        # block the thread until there are zero running Micro's
        while True:
            # since a single Micro is limited to 10 seconds (time_limit), we can get all
            # (possibly) running instances by subtracting 10 from the start time
            instances = self.base.fetch({"spawned_at?gte": self.start_time - self.time_limit, "running": True})

            # if there are no other running micro, we can start
            if instances.count == 0 and (time() - self.start_time) < 3:
                self.base.put(
                    {"running": True, "spawned_at": self.start_time}, key=self.key, expire_at=self.start_time + self.time_limit
                )
                # release thread
                return

            # sleep a bit to not overload Deta Base
            sleep(uniform(0.5, 2))
