# Python logged groups

This package designed to facilitate logging inside classes and functions with `@logged_group` decorator and also makes it possible
to manage logging level and any different things for any logging domain mentioned in log_cfg.json

This package maintained on [python-logged-groups github repsitory](https://github.com/rozhkovdmitrii/python-logged-groups) by rozhkovdmitrii<rozhkovdmitrii@yandex.ru> 

## Build package

To build package `dist/logged-groups-2.1.0.tar.gz`, for example, use following command:

```
python setup.py sdist
```

## Installation 

Then you can install package with the following:

```
pip install dist/logged-groups-2.1.0.tar.gz
```

or install it from pypi:

```
pip install logged-groups==2.1.0
```

or you can install it from git in your **requirements.txt**

```
git+https://github.com/rozhkovdmitrii/python-logged-groups.git@2.1.0
```

## Config file

There should be `log_cfg.json` in where you use `logged_groups` package. It's actually [standard configuration](https://docs.python.org/3/library/logging.config.html#configuration-functions) to be used with `logging.config.dictConfig`:
As you can see there are some irregular things:

* `logged_groups.ColoredFormatter` - to provide colored output
* `logged_groups.logging.ContextFilter` filter - to provide "%(context)s" in the related format string. That format won't work if this filter is not set.
* `neon` logger - parental umbrella logger gathers rules for `neon.funcs` and `neon.classes` loggers to avoid rules duplication

```json
{
    "version": 1,
    "handlers": {
        "colored": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",
            "filters": ["context_filter"]
        }
    },
    "filters": {
        "context_filter": {
            "()": "logged_groups.logging.ContextFilter"
        }
    },
    "formatters": {
        "colored": {
            "class": "logged_groups.ColoredFormatter",
            "format": "%(asctime)23s %(levelname)8s %(process)6d:%(threadName)-10s %(name)20s:%(class)-30s  %(context)s %(message)s",
            "style": "%"
        }
    },
    "loggers": {
        "neon": {
            "level": "DEBUG",
            "handlers": ["colored"],
            "filters": ["context_filter"],
            "propagate": false
        },
        "root": {
            "filters": ["context_filter"],
            "level": "DEBUG",
            "handlers": ["colored"],
            "propagate": false
        }
    }
}
```

## Logging group feature

`logged_group` decorator is designed to extend your classes and functions with a single logger that is not related to the name of module that is containing them.
From now on it is possible to group logging notes, logged  classes and logged functions in any module with a single logging group and, as a consequence, with a single logger. 
`logged_group` also extends a structure of logs with new logging attributes `class-name` and `class-id`.  
For each logger related to `logged_group` decorator you can set up different logging levels and others in configuration like for a standard logger. 


## Logging context feature

For each `logged_group`-related logger the `context` logging record attribute is available to use in a format string. 
That context gets started to be available after using it in source code in the following way:

```python 
from logged_groups import logging_context
with logging_context(ctx1="value", ctx2="other value"):
    # here the first logging context is available
    with logging_context(ctx3="value"):
        # here the second extended with ctx3 logging context is available
    # here the first logging context is back 
```


## Sample

```python
import threading
from logged_groups import logged_group, logging_context
import time


@logged_group("neon.classes")
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


@logged_group("classes")
class B:
    def __init__(self):
        for i in range(0, 5):
            self.debug("Spam spam spam spam spam ")


@logged_group("funcs")
def check_logger(*, logger):
    logger.info("Hoooray it's working!!!")


@logged_group("neon.funcs")
def parallel(*, logger):
    a = A(class_id=33)
    with logging_context(user_id="Max", mode="threaded"):
        try:
            for i in range(1, 10):
                time.sleep(1)
                a.do_stuff(i)
                if i == 5:
                    raise Exception("Something wrong")
        except Exception as e:
            logger.error(f"Got exception: \"{e}\"")
    a.do_stuff(777)


if __name__ == "__main__":
    a = A(class_id=33)

    tr = threading.Thread(target=parallel)
    tr.start()
    with logging_context(user_id="Alice") as ctx:
        a1 = A(class_id="1")
        a1.do_stuff(100)
        time.sleep(4)
        with logging_context(req_id="1", mode="support"):
            a1.do_stuff(101)
            a1.do_stuff(1001)
        a1.do_stuff(0)
    time.sleep(2)
    with logging_context(user_id="Bob", req_id="2", mode="processing"):
        b = B()
    time.sleep(2)
    check_logger()
    tr.join()
```
