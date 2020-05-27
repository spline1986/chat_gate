#!/usr/bin/env python3

from bottle import route, run, static_file


@route("/files/<filename>")
def static_file(filename):
    return static_file(filename, root="/files")

run(host="localhost", port="61234", quiet=True)
