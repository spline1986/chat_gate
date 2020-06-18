#!/usr/bin/env python3

from bottle import route, run, static_file


@route("/files/<filepath:path>")
def files(filepath):
    return static_file(filepath, root="files")


@route("/logs/<filename>")
def log(filename):
    return static_file(filename, root="logs")


run(host="localhost", port="61234", quiet=True)
