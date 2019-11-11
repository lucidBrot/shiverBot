#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# This file is a python2 wrapper for the python3 file query.py
# YES, this is a bad idea and the python2 files should be migrated to python3 ;)
import subprocess
from subprocess import CalledProcessError
from pipes import quote

def query(email, limit = 50):
    try:
        email = email.replace('\\', '\\\\').replace("'", r"\'").replace('"', r'\"')
        script = [
                "python3.6", 
                "-c", 
                    u"import query; print( query.query_by_email('{email}', {limit}) )".format(email = email, limit = limit)
            ]
        proc = subprocess.check_output(script, shell=False) 
        return proc
    except CalledProcessError as e:
        return "Could not access the database at this time."
