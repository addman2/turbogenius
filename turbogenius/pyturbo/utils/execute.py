#!python -u
# -*- coding: utf-8 -*-

"""

pyturbo: execute, methods to launch turborvb commands on a local machine

Todo:
    * docstrings are not completed.

"""

from __future__ import print_function

# python modules
import os
import sys
import re
import subprocess
from typing import Optional

# set logger
from logging import getLogger

logger = getLogger("pyturbo").getChild(__name__)


def run(
    binary: str, input_name: Optional[str] = None, output_name: str = "out.o"
):
    sys_env = os.environ.copy()
    if input_name is None:
        cmd = f"{binary} > {output_name}"
    else:
        cmd = f"{binary} < {input_name} > {output_name}"
    # p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True, env=my_env)
    # logger.info(p.stdout.decode())
    # logger.info(p.stderr.decode())

    logger.info(f"Execute command(s): {cmd}")

    if sys.platform == "darwin":
        if "LD_LIBRARY_PATH" in sys_env:
            if re.match(r".*bash.*", sys_env["SHELL"]) or re.match(
                r".*zsh.*", sys_env["SHELL"]
            ):
                cmd = f"export LD_LIBRARY_PATH={sys_env['LD_LIBRARY_PATH']} && {cmd}"
            elif re.match(r".*csh.*", sys_env["SHELL"]) or re.match(
                r".*tcsh.*", sys_env["SHELL"]
            ):
                cmd = f"setenv LD_LIBRARY_PATH {sys_env['LD_LIBRARY_PATH']} && {cmd}"
            else:
                raise NotImplementedError
        if "DYLD_LIBRARY_PATH" in sys_env:
            if re.match(r".*bash.*", sys_env["SHELL"]) or re.match(
                r".*zsh.*", sys_env["SHELL"]
            ):
                cmd = f"export DYLD_LIBRARY_PATH={sys_env['DYLD_LIBRARY_PATH']} && {cmd}"
            elif re.match(r".*csh.*", sys_env["SHELL"]) or re.match(
                r".*tcsh.*", sys_env["SHELL"]
            ):
                cmd = f"setenv DYLD_LIBRARY_PATH {sys_env['DYLD_LIBRARY_PATH']} && {cmd}"
            else:
                raise NotImplementedError

    subprocess.check_call(cmd, shell=True, env=sys_env)
