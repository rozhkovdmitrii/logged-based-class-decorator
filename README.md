# Python logged groups

This package designed to facilitate logging inside classes and functions with `@logged_group` decorator and also makes it possible
to manage logging level and any different things for any logging domain mentioned in log_cfg.json

This package maintained on [python-logged-groups github repsitory](https://github.com/rozhkovdmitrii/python-logged-groups) by rozhkovdmitrii<rozhkovdmitrii@yandex.ru> 

## Build package

To build package `dist/logged-groups-2.0.3.tar.gz`, for example, use following command:

```
python setup.py sdist
```

## Installation 

Then you can install package with the following:

```
pip install dist/logged-groups-2.0.3.tar.gz
```

or install it from pypi:

```
pip install logged-groups==2.0.3
```

or you can install it from git in your **requirements.txt**

```
git+https://github.com/rozhkovdmitrii/python-logged-groups.git@2.0.3
```

## Config file

There should be `log_cfg.json` in where you use `logged_groups` package. It's actually [standard configuration](https://docs.python.org/3/library/logging.config.html#configuration-functions) to be used with `logging.config.dictConfig`:
As you can see there is using `logged_groups.ColoredFormatter` to provide colored output

```json
{
    "version": 1,
    "handlers": {
        "colored": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored"
        }
    },
    "formatters": {
        "colored": {
            "class": "logged_groups.ColoredFormatter",
            "format": "%(asctime)23s %(levelname)8s %(process)6d:%(threadName)-10s %(name)20s:%(class)-30s %(message)s",
            "style": "%"
        }
    },
    "loggers": {
        "neon": {
            "level": "DEBUG",
            "handlers": ["colored"],
            "propagate": false
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["colored"],
            "propagate": false
        }
    }
}
```

## Using example

```python
from logged_groups import logged_group


@logged_group("neon.a")
class A:

    def __init__(self, **kws):
        self.info("Some information, keep focused on it")
        self.c = C(class_id="SingleC")

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


@logged_group("neon.log_group")
class C:

    def __init__(self, **kws):
        self.info("C class construtor")


@logged_group("neon.spam_group")
class B:
    def __init__(self):
        for i in range(0, 10):
            self.debug("Spam spam spam spam spam ")


@logged_group("log_group")
def check_logger(*, logger):
    logger.info("Hoooray it's working!!!")


if __name__ == "__main__":
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
```
