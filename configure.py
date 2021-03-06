# coding:utf-8
import sys
import os
from copy import copy
from optparse import OptionParser, Option, OptionValueError
import re
from collections import OrderedDict
import subprocess
import codecs
import json
from win32api import GetFileVersionInfo, LoadResource, LoadLibrary
import win32con


def is_patched(filename):
    lang, codepage = GetFileVersionInfo(
        filename, '\\VarFileInfo\\Translation')[0]
    strInfoPath = '\\StringFileInfo\\%04X%04X\\PatchedBy' % (lang, codepage)
    info = GetFileVersionInfo(filename, strInfoPath)

    if info:
        # print(filename + ": " + strInfoPath)
        # print(info)
        return True
    else:
        return False


def get_prefix(filename):
    m = LoadLibrary(filename)
    res = LoadResource(m, win32con.RT_STRING, 26)
    # index = 0
    # for line in prefix.decode('utf-16').split('\0'):
    #     print(str(index) + ":" + line + "\r\n")
    #     index = index + 1
    prefix = res.decode('utf-16').split('\0')[8]
    prefix = prefix.replace('\n', '\\n').replace('\0', '\\0')
    return prefix


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


def Main(filepath=None,
         showExcludes=None,
         hostfilter=[],
         targetfilter=[],
         langfilter=[],
         remark=None,
         debug=False):
    command = os.path.join(os.getenv("ProgramFiles(x86)"),
                           "Microsoft Visual Studio\\Installer\\vswhere.exe")
    if os.path.exists(command) is False:
        return "Can not find " + command
    command_with_args = " ".join([command,
                                 "-products *",
                                  "-requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                                  "-property installationPath",
                                  "-utf8"])
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
        if sys.version_info[0] == 3:
            line = line.decode("utf-8")
        vs_paths.append(line)
    print("Found VS installed in: \r\n\t" + "\r\n\t".join(vs_paths))

    json_obj = OrderedDict()
    vs_paths_switch = OrderedDict()
    if remark:
        json_obj["remark"] = remark
    json_obj["switch"] = vs_paths_switch

    for vs_path in vs_paths:
        vs_paths_switch[vs_path] = True
    config_file_path = filepath if filepath is not None else "template.json"
    config_file = codecs.open(
        config_file_path, "w", encoding="utf-8")
    host_filter = [x.lower()
                   for x in hostfilter] if hostfilter is not None else []
    target_filter = [x.lower()
                     for x in targetfilter] if targetfilter is not None else []
    lang_filter = langfilter if langfilter is not None else []
    filters = {"host": host_filter,
               "target": target_filter,
               "lang": lang_filter}
    if showExcludes is not None:
        print("FilterOut Mode is ON:")
        print(json.dumps(filters, indent=4, separators=(',', ': ')))
    for vs_path in vs_paths:
        vs_path_cfg = OrderedDict()
        relpaths = []
        relpaths_excludes = []
        files = find_files("clui.dll", vs_path)
        print("  find clui in Path: " + vs_path)
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

                patched = is_patched(file)
                patchflag = None
                if patched:
                    patchflag = '[Yes]'
                else:
                    patchflag = '[No]'
                prefix = get_prefix(file)

                if in_hosts and in_target and in_lang:
                    # print("\t{}\t{}\t{}".format(relpath, patchflag, prefix))
                    print("\t{}\t{}\t".format(relpath, patchflag)+prefix)
                    relpaths.append(relpath)
                else:
                    if debug is True:
                        print("\t{} {} {} {}".format(
                            relpath, in_hosts, in_target, in_lang))
                    if showExcludes is not None:
                        relpaths_excludes.append(relpath)
            else:
                print("Unknow format path: " + file)
        vs_path_cfg["root_path"] = vs_path
        vs_path_cfg["filters"] = filters
        vs_path_cfg["clui_list"] = relpaths
        vs_path_cfg["clui_list_excludes"] = relpaths_excludes
        # print(vs_path_cfg)
        json_obj[vs_path] = vs_path_cfg
    json_obj["custom_list"] = []
    rc = json.dump(json_obj, config_file,
                   indent=4, separators=(',', ': '))

    config_file.close()
    return rc


if __name__ == '__main__':
    parser = OptionParser(option_class=ListOption)

    parser.add_option('-f', '--file', type="string",
                      action='store', dest='file', 
                      help='where to save the config file. (default "template.json")')
    parser.add_option('-S', '--showExcludes',
                      action='store_true', dest='showExcludes',
                      help='enable to show the paths that have been filtered by the filtering options. (default not)')
    parser.add_option('-H', '--host', type="strlist",
                      action='store', dest='host',
                      help='host filter, can be x64,x86 . if not set, all host been accepted')
    parser.add_option('-T', '--target', type="strlist",
                      action='store', dest='target',
                      help='target filter, can be x64,x86 . if not set, all target been accepted')
    parser.add_option('-L', '--lang', type="intlist",
                      action='store', dest='lang',
                      help='Lang ID filter, it\'s a number, see the README.md about "Lang ID" . if not set, all lang been accepted')
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug')
    (options, args) = parser.parse_args()
    if args:
        print('ERROR: extra unparsed command-line arguments:', args)
        sys.exit(1)
    print('options: ' + str(options))
    sys.exit(Main(
        filepath=options.file,
        showExcludes=options.showExcludes,
        hostfilter=options.host,
        targetfilter=options.target,
        langfilter=options.lang,
        remark={'cmd': " ".join(sys.argv)},
        debug=options.debug,
    ))
