#!/usr/bin/env python3

from bottle import route, run, static_file


@route("/files/<filename>")
def files(filename):
    return static_file(filename, root="files")


@route("/logs/<filename>")
def log(filename):
    return static_file(filename, root="logs")


run(host="localhost", port="61234", quiet=True)
