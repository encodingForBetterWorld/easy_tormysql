import sys

py3 = sys.version_info[0] >= 3
coroutine, Return, pyield = None, None, py3 and "yield from" or "yield"
try:
    import asyncio

    coroutine = asyncio.coroutines.coroutine
except ImportError:
    from tornado.gen import coroutine

    coroutine = coroutine

try:
    import tornado.gen

    Return = tornado.gen.Return
except ImportError:
    pass


def pret(ret="ret"):
    if py3:
        return "return %s" % ret
    else:
        return "raise Return(%s)" % ret
