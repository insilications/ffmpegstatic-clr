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
    libs_re = re.compile(r"(extralibs_)(|avutil|avcodec|avformat|avdevice|avfilter|avresample|postproc|swscale|swresample)(?==)")
    libs_files_re = re.compile(r"(-l[a-zA-Z0-9_\s\-\.+\/]*|-p[a-zA-Z0-9_\s\-\.+\/]*)")
    lib_list_re_exclude = re.compile(r"(-pthread|-L[a-zA-Z0-9_\-+\/.]*)")
    lib_list_re_try = re.compile(r"(?<=-l)[a-zA-Z0-9_\-+\/.]*")
    libs_dict = defaultdict(list)
    if os.path.exists(libs_file):
        with open_auto(libs_file, 'r') as libs:
                libs_lines = libs.readlines()
                # print("{} \n".format(libs_lines))
                for line in libs_lines:
                    # print("{} \n".format(line))
                    # print("{} = {} \n".format(re.search(libs_re, line).group(0), re.search(libs_files_re, line).group(0).split()))
                    # libs_dict[re.search(libs_re, line).group(0)] = re.search(libs_files_re, line).group(0).split()
                    libs_files_list = re.search(libs_files_re, line).group(0).split()
                    for lib in libs_files_list:
                        if re.search(lib_list_re_exclude, lib):
                            print("exclude: {}".format(lib))
                            continue
                        if re.search(lib_list_re_try, lib):
                            lib_file_re = "lib{}".format(re.search(lib_list_re_try, lib).group(0))
                            print("try: {}.a".format(lib_file_re))
                            # print("Command: {}".format(rg_command))
                            usr_re = re.compile("^/(usr/|usr.*)(lib|lib64)/[a-zA-Z0-9._+-]*{}\.a$".format(lib_file_re))
                            for dirpath, dirnames, filenames in os.walk("/usr/lib64", followlinks=True):
                                for filename in filenames:
                                    if usr_re.match(os.path.join(dirpath, filename)):
                                        print("Found usr_re: {}".format(filename))
                            rg_command = "rg --no-line-number --no-filename --pcre2 '^/(usr/|usr.*)(lib|lib64)/[a-zA-Z0-9._+-]*lib{}\.a$'".format(lib_file_re)
                            try:
                                process = subprocess.run(rg_command, check=True, shell=True, stdout=subprocess.PIPE, text=True, universal_newlines=True, cwd="/insilications/build/clearlinux/packages")
                            except subprocess.CalledProcessError as err:
                                # print_fatal("Not found {}: {}".format(rg_command, err))
                                continue
                            print("Found rg: {}".format(process.stdout.rstrip("\n")))
                            # print("Found: {}".format(process.stdout.rstrip("\n")))


if __name__ == '__main__':
    main()