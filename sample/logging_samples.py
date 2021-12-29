import threading

from logged_groups import logged_group


@logged_group("log_group")
class A:

    def __init__(self, **kws):
        self.info("Some information, keep focused on it")

    def do_stuff(self, value: int):
        try:
            self._do_stuff_impl(value)
        except BaseException as e:
            self.error(f"Failed to do stuff because of error: {e}")

    def _do_stuff_impl(self, value):
        self.debug(f"Doing stuff with value: {value}")
        if value > 1000:
            raise Exception(f"Value critically high: {value}")

        if value > 100:
            self.warning(f"Value higher than 100, it can be wrong: {value}")


@logged_group("other_log_group")
class B:

    def __init__(self):
        self.debug("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")
        self.error("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")
        self.debug("Spam spam spam spam spam ")


@logged_group("log_group")
def check_logger():
    logger.info("Hoooray it's working!!!")


if __name__ == "__main__":
    threading.current_thread().name = "main"
    a1 = A(class_id="1")
    a1.do_stuff(100)
    a1.do_stuff(101)
    a1.do_stuff(1001)

    b = B()

    a2 = A(class_id="2")
    a2.do_stuff(100)
    a2.do_stuff(101)
    a2.do_stuff(1001)

    check_logger()

