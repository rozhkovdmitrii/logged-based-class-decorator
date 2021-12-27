# Logged based class

This distributed library distinct to be used in

## Build package

To build package `dist/logged-based-class-1.0.tar.gz`, for example, use following command:

```
python setup.py sdist
```

## Installation 

Then you can install package with the following:

```
pip install logged-based-class-1.0.tar.gz
```

## Config file

There should be `log_cfg.json` in where you use `logged_based_class`. It can look like:

```json
{
  "format": null,
  "colored": true,
  "groups": {
    "log_group": "DEBUG",
    "other_log_group": "DEBUG"
  }
}
```

## Using example

```python
import threading

from logged_based_class import logged_based


@logged_based("log_group")
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


@logged_based("other_log_group")
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
```
