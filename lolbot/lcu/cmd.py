"""
Get league of legends auth url from process info
"""

import re
from dataclasses import dataclass

import psutil

from lcu_api import LCUError


LCU_PORT_KEY = "--app-port="
LCU_TOKEN_KEY = "--remoting-auth-token="

PORT_REGEX = re.compile(r"--app-port=(\d+)")
TOKEN_REGEX = re.compile(r"--remoting-auth-token=(\S+)")

PROCESS_NAME = "LeagueClientUx.exe"


@dataclass
class CommandLineOutput:
    auth_url: str = ""
    token: str = ""
    port: str = ""


def get_commandline() -> CommandLineOutput:
    """
    Retrieves the command line of the LeagueClientUx.exe process and
    returns the relevant information
    """
    try:
        # Iterate over all running processes
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] == PROCESS_NAME:
                cmdline = " ".join(proc.info['cmdline'])
                return match_stdout(cmdline)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        raise LCUError(f"Process handling error: {str(e)}")


def match_stdout(stdout: str) -> CommandLineOutput:
    """Parses the command line string to extract port, token, and directory"""
    port_match = PORT_REGEX.search(stdout)
    port = port_match.group(1).replace(LCU_PORT_KEY, '') if port_match else "0"

    token_match = TOKEN_REGEX.search(stdout)
    token = token_match.group(1).replace(LCU_TOKEN_KEY, '').replace('"', '') if token_match else ""

    auth_url = f"https://riot:{token}@127.0.0.1:{port}"

    return CommandLineOutput(auth_url=auth_url, token=token, port=port)
