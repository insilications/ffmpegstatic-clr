#!/usr/bin/python3

import argparse
import os
import re
import subprocess
import sys
import textwrap
import hashlib
import shlex
import sys
from collections import defaultdict


def write_out(filename, content, mode="w"):
    """File.write convenience wrapper."""
    with open_auto(filename, mode) as require_f:
        require_f.write(content)


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--libfile", dest="libs_file", action="store", default="ffbuild/libs.mak", help="Set lib file to use")
    args = parser.parse_args()
    libs_file = args.libs_file

    libs_re = re.compile(r"(?<=EXTRALIBS-)(|avutil|avcodec|avformat|avdevice|avfilter|avresample|postproc|swscale|swresample|cpu_init|cws2fws|ffplay|ffprobe|ffmpeg)(?==)")
    libs_files_re = re.compile(r"(?<==).+$")
    lib_list_re_exclude = re.compile(r"(-pthread|-L[a-zA-Z0-9_\-+\/.]*)")
    lib_list_re_try = re.compile(r"(?<=-l)[a-zA-Z0-9_\-+\/.]*")
    libs_dict = defaultdict(list)

    libs_out_file = os.path.join(os.path.dirname(libs_file), 'libs_var.sh')
    if os.path.exists(libs_out_file):
        os.remove(libs_out_file)

    if os.path.exists(libs_file):
        with open_auto(libs_file, 'r') as libs:
                libs_lines = libs.readlines()
                # print("{} \n".format(libs_lines))
                for line in libs_lines:
                    # print("{} \n".format(line))
                    # print("{} = {} \n".format(re.search(libs_re, line).group(0), re.search(libs_files_re, line).group(0).split()))
                    # libs_dict[re.search(libs_re, line).group(0)] = re.search(libs_files_re, line).group(0).split()
                    ff_lib = re.search(libs_re, line).group(0)
                    found = ""
                    # print("{} \n".format(re.search(libs_re, line).group(0)))
                    match = re.search(libs_files_re, line)
                    if not match:
                        continue
                    libs_files_list = match.group(0).split()
                    for lib in libs_files_list:
                        if re.search(lib_list_re_exclude, lib):
                            libs_dict[ff_lib].append(lib)
                            # print("exclude: {}".format(lib))
                            continue
                        if re.search(lib_list_re_try, lib):
                            lib_file_pre = re.search(lib_list_re_try, lib).group(0)
                            lib_file_re_s = "lib{}".format(lib_file_pre)
                            lib_file_re = re.escape(lib_file_re_s)
                            compile_usr_re = r"^/(usr/|usr.*)(lib|lib64)/[a-zA-Z0-9._+-]*{}\.a$".format(lib_file_re)
                            usr_re = re.compile(compile_usr_re)
                            breakIt = False
                            for dirpath, dirnames, filenames in os.walk("/usr/lib64", followlinks=True):
                                if breakIt == False:
                                    for filename in filenames:
                                        if breakIt == False:
                                            full_match = os.path.join(dirpath, filename)
                                            if usr_re.match(full_match):
                                                libs_dict[ff_lib].append(full_match)
                                                # print("Found usr_re: {}".format(full_match))
                                                breakIt = True
                                        else:
                                            break
                                else:
                                    break
                            for dirpath, dirnames, filenames in os.walk("/usr/lib", followlinks=True):
                                if breakIt == False:
                                    for filename in filenames:
                                        if breakIt == False:
                                            full_match = os.path.join(dirpath, filename)
                                            if usr_re.match(full_match):
                                                libs_dict[ff_lib].append(full_match)
                                                # print("Found usr_re: {}".format(full_match))
                                                breakIt = True
                                        else:
                                            break
                                else:
                                    break
                            # print_fatal("Not found {}: {}".format(rg_command, err))
                            if (breakIt == False):
                                libs_dict[ff_lib].append("-l{}".format(lib_file_pre))
                    print("{}_extralibs=\"{}\"".format(ff_lib, " ".join(libs_dict[ff_lib])))
                    print("\n\n")
                    write_out(libs_out_file, '{}_extralibs=\"{}\"\n'.format(ff_lib, " ".join(libs_dict[ff_lib])), "a")


if __name__ == '__main__':
    main()