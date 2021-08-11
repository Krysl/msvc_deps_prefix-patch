import sys
import codecs
import re


def Main(src, dst, path):
    # `		VALUE "OriginalFilename", "CLUI.DLL"`
    OriginalFilename = re.compile(
        r"(.*)\"OriginalFilename\"(.*)")
    rf = codecs.open(
        src, encoding="utf-16")
    found = False
    lines = []
    for line in rf:
        # print(type(line))
        # print(line)
        m = OriginalFilename.match(line)
        if m is None:
            lines.append(line)
            continue
        found = True
        lines.append(line)
        lines.append('		VALUE "PatchedBy", "https://github.com/Krysl/msvc_deps_prefix-patch"\r\n')
        lines.append('		VALUE "OriginalPath", "{}"\r\n'.format(path.replace('\\', '/')))
    if found is True:
        wf = codecs.open(dst, "w", encoding=rf.encoding)
        wf.write("".join(lines))
        wf.close()
    else:
        return "Can Not find msvc_deps_prefix in " + src


if __name__ == '__main__':
    sys.exit(Main(sys.argv[1], sys.argv[2], sys.argv[3]))
