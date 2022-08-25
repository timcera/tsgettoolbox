# -*- coding: utf-8 -*-

import shlex
import subprocess
import sys

from setuptools import setup

pkg_name = "tsgettoolbox"

version = open("VERSION", encoding="ascii").readline().strip()

if sys.argv[-1] == "publish":
    subprocess.run(shlex.split("cleanpy ."), check=True)
    subprocess.run(shlex.split("python setup.py sdist"), check=True)
    subprocess.run(
        shlex.split(f"twine upload dist/{pkg_name}-{version}.tar.gz"), check=True
    )
    sys.exit()

setup()
