# coding:utf-8
import sys
import os
from optparse import OptionParser, Option, OptionValueError
import codecs
import json
import re
from hashlib import md5
from win32api import GetFileVersionInfo


def is_patched(filename):
    lang, codepage = GetFileVersionInfo(
        filename, '\\VarFileInfo\\Translation')[0]
    strInfoPath = '\\StringFileInfo\\%04X%04X\\PatchedBy' % (lang, codepage)
    info = GetFileVersionInfo(filename, strInfoPath)

    if info:
        return True
    else:
        return False


def get_clui_lists(cfg_json=None):
    clui_list = []
    # print(cfg_json)
    switch = cfg_json['switch']
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

    for path in switch:
        if switch[path] is False:
            continue
        pathcfg = cfg_json[path]
        # print(pathcfg)
        lang = pathcfg['lang'] if 'lang' in pathcfg else []
        host = pathcfg['host'] if 'host' in pathcfg else []
        target = pathcfg['target'] if 'target' in pathcfg else []

        host_filter = [x.lower() for x in host]
        target_filter = [x.lower() for x in target]
        lang_filter = [int(lang) for x in lang]

        for subpath in pathcfg['clui_list']:

            m = filefilter.match(subpath)

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
                    fullpath = path + '\\' + subpath
                    fullpath = os.path.normpath(fullpath)
                    if os.path.exists(fullpath) and not is_patched(fullpath):
                        print("\t{}".format(fullpath))
                        clui_list.append(fullpath)
            else:
                print("Unknow format path: " + subpath)

    for path in cfg_json['custom_list']:
        if os.path.exists(path):
            clui_list.append(path)

    return clui_list


def get_lang(filename):
    lang, _ = GetFileVersionInfo(
        filename, '\\VarFileInfo\\Translation')[0]
    return lang


def gen_ninja_configs(file):
    print('gen_ninja_configs: '+file)
    hashcode = md5(file).hexdigest()
    folder = 'out/' + hashcode
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = hashcode
    lang = str(get_lang(file))
    escape_file = file.replace(':', '$:').replace(' ', '$ ')

    file_template = """
ninja_required_version = 1.7.2

include toolchain.ninja

build {path}/clui.rc: rh_get_rc {path}/clui.original.dll
build {path}/clui.ver.rc: rh_get_ver_rc {path}/clui.original.dll

build {path}/clui.modified.rc: modify_rc {path}/clui.rc
build {path}/clui.modified.ver.rc: modify_ver_rc {path}/clui.ver.rc
  original_path = "{file}"

build {path}/clui.res: rh_compile_rc_to_res {path}/clui.modified.rc
build {path}/clui.ver.res: rh_compile_rc_to_res {path}/clui.modified.ver.rc

build {path}/clui.rh {path}/clui.log: rh_gen_rhscript {path}/clui.res {path}/clui.ver.res
  src_dll = {path}/clui.original.dll
  dist_dll = {path}/clui.dll
  langid = {lang}
  rh_log = {path}/clui.log

build {path}/clui.dll: rh_gen_dll $
  {path}/clui.rh

build {path}/clui.original.dll: copy {escape_file}

build {hashcode}: phony $
  {path}/clui.dll


## belows for install
#build admin_install: install {path}/clui.dll
#  dst = "{file}"
#  timefile = "{file}"
#
#default all
""".replace('{file}', file).replace('{path}', path).replace('{escape_file}', escape_file).replace('{lang}', lang).replace('{hashcode}', hashcode)
    # print(file_template)
    build_ninja_path = os.path.join(folder, 'build.ninja')
    build_ninja = codecs.open(build_ninja_path, "w", encoding="utf-8")
    build_ninja.write(file_template)
    build_ninja.close()
    return (os.path.join(hashcode, 'build.ninja'), '{}/clui.dll'.format(path), file)


def gen_toolchain_ninja(path):
    ResourceHacker = path + '/tools/ResourceHacker/ResourceHacker.exe'
    gsudo = path + '/tools/gsudo/gsudo.exe'
    template = """
rule copy
  command = cmd /c python "{path}/scripts/cp.py" ${in} ${out}
  description = copy ${in} ${out}

rule install
  command = gsudo python "scripts/sudo_cp.py" ${in} ${dst} ${out} ${timefile}
  description = install ${in} to ${dst}

rule rh_get_rc
  command = ResourceHacker -open ${in}  -save ${out} -action extract "String Table" -mask STRINGTABLE,26,
  description = get rc from ${in}, save as ${out}

rule rh_get_ver_rc
  command = ResourceHacker -open ${in}  -save ${out} -action extract "Version Info" -mask VERSIONINFO,1,
  description = get rc from ${in}, save as ${out}

rule modify_rc
  command = cmd /c python {path}/scripts/rc_modify.py  ${in} ${out}
  description = modify msvc_deps_prefix in ${in}, save to ${out}

rule modify_ver_rc
  command = cmd /c python {path}/scripts/ver_rc_modify.py  ${in} ${out} ${original_path}
  description = modify version in ${in}, save to ${out}

rule rh_compile_rc_to_res
  command = ResourceHacker -open ${in} -save ${out} -action compile

rule rh_gen_rhscript
  command = {path}/scripts/gen_rh_script.bat ${src_dll} ${in} ${langid} ${dist_dll} ${out} ${rh_log}

rule rh_gen_dll
  command = {path}/scripts/gen_dll.bat ${in} ${out}
  description = gen dll: ${out}

""".replace('{path}', path).replace('ResourceHacker', ResourceHacker).replace('gsudo', gsudo)

    toolchain_ninja_path = os.path.join('out', 'toolchain.ninja')
    toolchain_ninja = codecs.open(
        toolchain_ninja_path, "w", encoding="utf-8")
    toolchain_ninja.write(template)
    toolchain_ninja.close()


def gen_install_script(pathlist):
    print(pathlist)
    install_path = os.path.join('.', 'install.bat')
    install = codecs.open(install_path, "w", encoding="utf-8")
    install.write('@REM Run this with administrator permission\r\n')
    for _, src, dst in pathlist:
        install.write('copy /Y "out\{}" "{}"\r\n'.format(src.replace('/', '\\'), dst))
    install.write('\r\n')
    install.close()

    admin_install_path = os.path.join('.', 'admin_install.bat')
    admin_install = codecs.open(admin_install_path, "w", encoding="utf-8")
    admin_install.write(r' %~dp0\tools\gsudo\gsudo.exe %~dp0\install.bat')
    admin_install.close()


def gen_ninja_configs_foreach(filelist):
    build_ninja_list = []
    for file in filelist:
        build_ninja_path = gen_ninja_configs(file)
        build_ninja_list.append(build_ninja_path)

    root_build_ninja_path = os.path.join('out', 'build.ninja')
    build_ninja = codecs.open(root_build_ninja_path, "w", encoding="utf-8")
    build_ninja.write('ninja_required_version = 1.7.2\n\n')
    for file, _, _ in build_ninja_list:
        build_ninja.write('subninja {}\n'.format(file.replace('\\', '/')))
    build_ninja.write('\n')

    build_ninja.write('build all: phony ')
    for file, _, _ in build_ninja_list:
        hashcode = os.path.dirname(file)
        build_ninja.write('$\n  {} '.format(hashcode))

    build_ninja.write('\n\n')
    build_ninja.write('default all')
    build_ninja.write('\n')
    build_ninja.close()

    gen_toolchain_ninja(os.path.dirname(os.path.abspath(__file__)))

    gen_install_script(build_ninja_list)


def Main(config=None):
    config_file_path = config if config is not None else "config.json"
    config_file = codecs.open(
        config_file_path, "r", encoding="utf-8")
    # lines = config_file.readlines()
    # print(lines)
    cfg_json = json.load(config_file)

    clui_list = get_clui_lists(cfg_json)

    gen_ninja_configs_foreach(clui_list)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--cfg', type="string",
                      action='store', dest='cfg')
    (options, args) = parser.parse_args()
    if args:
        print('ERROR: extra unparsed command-line arguments:', args)
        sys.exit(1)
    print('options: ' + str(options))
    sys.exit(Main(
        config=options.cfg
    ))
