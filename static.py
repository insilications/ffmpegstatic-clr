#!/usr/bin/python3

import configparser
import os
import re
import subprocess
import sys
import textwrap
import hashlib
import shlex
import sys
from collections import defaultdict

def open_auto(*args, **kwargs):
    """Open a file with UTF-8 encoding.

    Open file with UTF-8 encoding and "surrogate" escape characters that are
    not valid UTF-8 to avoid data corruption.
    """
    # 'encoding' and 'errors' are fourth and fifth positional arguments, so
    # restrict the args tuple to (file, mode, buffering) at most rg --only-matching -N -I dict
    assert len(args) <= 3
    assert 'encoding' not in kwargs
    assert 'errors' not in kwargs
    return open(*args, encoding="utf-8", errors="surrogateescape", **kwargs)


def main():
    libs_file = "/insilications/build/custom-apps/ffmpegstatic-clr/libs"
    libs_re = r"(extralibs_)(|avutil|avcodec|avformat|avdevice|avfilter|avresample|postproc|swscale|swresample)(?==)"
    libs_files_re = r"(-l[a-zA-Z0-9_\s\-\.+\/]*|-p[a-zA-Z0-9_\s\-\.+\/]*)"
    libs_dict = defaultdict(list)
    if os.path.exists(libs_file):
        with open_auto(libs_file, 'r') as libs:
                libs_lines = libs.readlines()
                # print("{} \n".format(libs_lines))
                for line in libs_lines:
                    # print("{} \n".format(line))
                    print("{} = {} \n".format(re.search(libs_re, line).group(0), re.search(libs_files_re, line).group(0).split()))
                    libs_dict[re.search(libs_re, line).group(0)] = re.search(libs_files_re, line).group(0).split()
                #print("{} \n".format(libs_dict))

if __name__ == '__main__':
    main()
