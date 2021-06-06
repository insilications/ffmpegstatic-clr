#!/usr/bin/python3

import argparse
import os
import re
import subprocess
import sys
import textwrap
import hashlib
import shlex
import mmap
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
    assert "encoding" not in kwargs
    assert "errors" not in kwargs
    return open(*args, encoding="utf-8", errors="surrogateescape", **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--libfile", dest="libs_file", action="store", default="ffbuild/libs.mak", help="Set lib file to use")
    args = parser.parse_args()
    libs_file = args.libs_file

    EXTRALIBSfile_re = re.compile(r"(?<=EXTRALIBS-)(?:sw(?:resamp|sca)le|av(?:filter|util)|avformat|c(?:pu_init|ws2fws)|(?:avdevic|ffprob)e|postproc|avcodec|ff(?:mpeg|play))")
    EXTRALIBSfile_line_re = re.compile(r"(?<==).+$")
    EXTRALIBSfile_line_exclude_re = re.compile(r"(-L[a-zA-Z0-9_\-+\/.]*|-W[a-zA-Z0-9_\-+\/.,]*)")
    EXTRALIBSfile_line_exclude_so_re = re.compile(r"\-(?:l(?:pthread|stdc\+\+|gcc|rt|GL|dl|[cm])|pthread)")

    EXTRALIBSfile_line_lib_re = re.compile(r"(?<=-l)[a-zA-Z0-9_\-+\/.]*")
    libs_dict = defaultdict(list)

    libs_file_out_file = os.path.join(os.path.dirname(libs_file), "libs_var.sh")
    if os.path.exists(libs_file_out_file):
        os.remove(libs_file_out_file)

    if os.path.exists(libs_file):
        with open_auto(libs_file, "r") as libs:
            libs_lines = libs.readlines()
            # print("{} \n".format(libs_lines))
            for libs_line in libs_lines:
                # print("{} \n".format(line))
                # print("{} = {} \n".format(re.search(libs_re, line).group(0), re.search(libs_files_re, line).group(0).split()))
                # libs_dict[re.search(libs_re, line).group(0)] = re.search(libs_files_re, line).group(0).split()
                ff_lib = re.search(EXTRALIBSfile_re, libs_line).group(0)
                # print("{} \n".format(re.search(libs_re, line).group(0)))
                libs_line_matched = re.search(EXTRALIBSfile_line_re, libs_line)
                if not libs_line_matched:
                    continue
                libs_line_matched_splitted = libs_line_matched.group(0).split()
                # print("libs_line_matched_splitted[{0}]: {1}".format(ff_lib, libs_line_matched_splitted))
                for lib in libs_line_matched_splitted:
                    if re.search(EXTRALIBSfile_line_exclude_re, lib):
                        libs_dict[ff_lib].append(lib)
                        continue
                        # print("exclude: {}".format(lib))
                    if re.search(EXTRALIBSfile_line_exclude_so_re, lib):
                        libs_dict[ff_lib].append("{}".format(lib))
                        continue
                        # print("exclude: {}".format(lib))
                    # for k, l in libs_dict.items():
                    #     print("libs_dict[{0}]: {1}".format(k, l))
                    if re.search(EXTRALIBSfile_line_lib_re, lib):
                        lib_matched = re.search(EXTRALIBSfile_line_lib_re, lib).group(0)
                        lib_matched_string = "lib{}".format(lib_matched)
                        print("lib_matched_string: {0}".format(lib_matched_string))
                        lib_matched_string_escaped = re.escape(lib_matched_string)
                        print("lib_matched_string_escaped: {0}".format(lib_matched_string_escaped))
                        # compile_usr_re = r"^/(usr|usr/[a-zA-Z0-9._+-\/]*)/(lib|lib64)/[a-zA-Z0-9._+-\/]*{}(\.a|_static\.a)$".format(lib_file_re)
                        # lib_matched_path_re =
                        test = r"{0}(\.a|_static\.a)$".format(lib_matched_string_escaped)
                        print(test)
                        lib_matched_path_re = re.compile(r"{0}(\.a|_static\.a)$".format(lib_matched_string_escaped))
                        # breakIt = False
                        # files = [f.name for f in os.scandir("/usr/local/cuda/lib64") if f.is_file() and os.path.splitext(f.name)[1].lower() in ".rpm"]
                        # for dirpath, dirnames, filenames in os.walk("/usr/cuda/lib64", followlinks=True):
                        #     if breakIt is False:
                        #         for filename in filenames:
                        #             if breakIt is False:
                        #                 full_match = os.path.join(dirpath, filename)
                        #                 if lib_matched_path_re.match(full_match):
                        #                     if (shared == 1) or (shared == 0):
                        #                         libs_dict[ff_lib].append("{} {}".format(Bstatic, full_match))
                        #                         # print("Found usr_re: {}".format(full_match))
                        #                         breakIt = True
                        #                         shared = 2
                        #                     else:
                        #                         libs_dict[ff_lib].append("{}".format(full_match))
                        #                         # print("Found usr_re: {}".format(full_match))
                        #                         breakIt = True
                        #                         shared = 2
                        #             else:
                        #                 break
                        #     else:
                        #         break
        # print('{}_extralibs="{}"'.format(ff_lib, " ".join(libs_dict[ff_lib])))
        # print("\n\n")
        # write_out(libs_file_out_file, '{}_extralibs="{}"\n'.format(ff_lib, " ".join(libs_dict[ff_lib])), "a")


if __name__ == "__main__":
    main()
