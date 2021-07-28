import sys
import os
from copy import copy
from optparse import OptionParser, Option, OptionValueError
import re
from collections import OrderedDict
import subprocess
import codecs
import json


def check_list(option, opt, value):
    try:
        return value.split(',')
    except ValueError:
        raise OptionValueError(
            "option %s: invalid complex value: %r" % (opt, value))


def check_intlist(option, opt, value):
    try:
        strlist = value.split(',')
        return [int(x) for x in strlist]
    except ValueError:
        raise OptionValueError(
            "option %s: invalid complex value: %r" % (opt, value))


class ListOption (Option):
    TYPES = Option.TYPES + ('list', 'intlist', 'strlist')
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER['list'] = check_list
    TYPE_CHECKER['intlist'] = check_intlist
    TYPE_CHECKER['strlist'] = check_list


def find_files(filename, search_path):
    result = []
    for root, dir, files in os.walk(search_path):
        if filename in files:
            result.append(os.path.join(root, filename))
    return result


def Main(showExcludes=None, hostfilter=[], targetfilter=[], langfilter=[], debug=False):
    command = os.path.join(os.getenv("ProgramFiles(x86)"),
                           "Microsoft Visual Studio\\Installer\\vswhere.exe")
    if os.path.exists(command) is False:
        return "Can not find " + command
    command_with_args = " ".join([command,
                                 "-products *",
                                  "-requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                                  "-property installationPath"])
    outputs = subprocess.check_output(command_with_args).splitlines()
    print(outputs)

    """ VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx64\\x64\\1033\\clui.dll """
    filefilter = re.compile(r"""
    ^(.*)\\                 # VC\\Tools\\MSVC\\
    (\d{2}\.\d{2}\.\d+)\\   # 14.29.30037\\
    bin\\                   # bin\\
    (Host[^\\]+)\\          # Hostx64 or Hostx86
    ([^\\]+)\\              # x64 or x86
    (\d{4,5})\\             # 1033 or 2052 or ... (Locale ID)
    clui.dll
    """, re.VERBOSE)

    vs_paths = []
    for line in outputs:
        exists = os.path.exists(line)
        if exists is False:
            continue
        vs_paths.append(line)
    print("Found VS installed in: \r\n\t" + "\r\n\t".join(vs_paths))

    json_obj = OrderedDict()
    vs_paths_switch = OrderedDict()
    json_obj["switch"] = vs_paths_switch

    for vs_path in vs_paths:
        vs_paths_switch[vs_path] = True
    config_file = codecs.open(
        "template.json", "w", encoding="utf-8")
    host_filter = [x.lower() for x in hostfilter] if hostfilter is not None else []
    target_filter = [x.lower() for x in targetfilter] if targetfilter is not None else []
    lang_filter = langfilter if langfilter is not None else []
    filters = {"host": host_filter,
               "target": target_filter,
               "lang": lang_filter}
    print(host_filter, target_filter, lang_filter)
    print(host_filter, target_filter, lang_filter)
    if showExcludes is not None:
        print("FilterOut Mode is ON:")
        print(json.dumps(filters, indent=4, separators=(',', ': ')))
    for vs_path in vs_paths:
        vs_path_cfg = OrderedDict()
        relpaths = []
        relpaths_excludes = []
        files = find_files("clui.dll", vs_path)
        print("  in Path: " + vs_path)
        for file in files:
            relpath = os.path.relpath(file, vs_path)
            m = filefilter.match(file)
            if(m):
                _, version, host, target, lang = m.groups()
                host = host.lstrip('Host').lower()
                target = target.lower()
                lang = int(lang)

                in_hosts = False
                if len(host_filter) == 0 or host in host_filter:
                    in_hosts = True

                in_target = False
                if len(target_filter) == 0 or target in target_filter:
                    in_target = True

                in_lang = False
                if len(lang_filter) == 0 or lang in lang_filter:
                    in_lang = True

                if in_hosts and in_target and in_lang:
                    print("\t" + relpath)
                    relpaths.append(relpath)
                else:
                    if debug is True:
                        print("\t{} {} {} {}".format(
                            relpath, in_hosts, in_target, in_lang))
                    if showExcludes is not None:
                        relpaths_excludes.append(relpath)
            else:
                print("Not match: " + file)
        vs_path_cfg["root_path"] = vs_path
        vs_path_cfg["filters"] = filters
        vs_path_cfg["clui_list"] = relpaths
        vs_path_cfg["clui_list_excludes"] = relpaths_excludes
        # print(vs_path_cfg)
        json_obj[vs_path] = vs_path_cfg
    rc = json.dump(json_obj, config_file,
                   indent=4, separators=(',', ': '))

    config_file.close()
    return rc


if __name__ == '__main__':
    parser = OptionParser(option_class=ListOption)
    parser.add_option('-S', '--showExcludes',
                      action='store_true', dest='showExcludes')

    parser.add_option('-H', '--host', type="strlist",
                      action='store', dest='host')
    parser.add_option('-T', '--target', type="strlist",
                      action='store', dest='target')
    parser.add_option('-L', '--lang', type="intlist",
                      action='store', dest='lang')
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug')
    (options, args) = parser.parse_args()
    if args:
        print('ERROR: extra unparsed command-line arguments:', args)
        sys.exit(1)
    print('options: ' + str(options))
    sys.exit(Main(showExcludes=options.showExcludes, hostfilter=options.host,
             targetfilter=options.target, langfilter=options.lang, debug=options.debug))
