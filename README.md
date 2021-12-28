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
  "logged_groups": {
    "log_group": "DEBUG",
    "other_log_group": "DEBUG"
  }
}
```

##### format

You can replace format string with your own. There also support extra logging attributes in addition to [standard ones](https://docs.python.org/3/library/logging.html#logrecord-attributes)

  * class - decorated with `logged_group` class name
  * class_id - class id set by `class_id` argument passed into constructor

```
{
  "format": "%(asctime)23s %(levelname)8s %(process)6d:%(threadName)-10s %(class)15s:%(class_id)-8s %(message)s",
  "colored": true,
  ...
}
```

##### colored

Optional. Default - `false`. If set output well be colored

##### propagation

Optional. Default - `false`. If set log messages will be propagated into parent logger if that are exists

##### logged_groups

Each pair in this dict is definition of logging group and level related to it.
So it gets possible to reduce logging level for classes related to this group and decorated with `@logged_group` in appropriate way in sources


## Using example

```python
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
