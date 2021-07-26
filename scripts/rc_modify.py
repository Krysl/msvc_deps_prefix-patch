import sys
import codecs
import re


def ints2bytes(ints):
    bytes = []
    for x in ints:
        if x >= 0:
            bytes.append(x)
        else:
            bytes.append(256+x)
    return bytes


langList = [
    ("en-US", bytearray(ints2bytes([78, 111, 116, 101, 58, 32, 105, 110, 99, 108, 117, 100, 105, 110, 103, 32, 102,
                                    105, 108, 101, 58])).decode(encoding="utf-8")),
    ("zh-TW", bytearray(ints2bytes([-26, -77, -88, -26, -124, -113, 58, 32, -27, -116, -123, -27, -112, -85, -26, -86,
                                    -108, -26, -95, -120, 58])).decode(encoding="utf-8")),
    ("cs-CZ", bytearray(ints2bytes([80, 111, 122, 110, -61, -95, 109, 107, 97, 58, 32, 86, -60, -115, 101, 116, 110,
                                    -60, -101, 32, 115, 111, 117, 98, 111, 114, 117, 58])).decode(encoding="utf-8")),
    ("de-DE", bytearray(ints2bytes([72, 105, 110, 119, 101, 105, 115, 58, 32, 69, 105, 110, 108, 101, 115, 101, 110,
                                    32, 100, 101, 114, 32, 68, 97, 116, 101, 105, 58])).decode(encoding="utf-8")),
    ("fr-FR", bytearray(ints2bytes([82, 101, 109, 97, 114, 113, 117, 101, -62, -96, 58, 32, 105, 110, 99, 108, 117,
                                    115, 105, 111, 110, 32, 100, 117, 32, 102, 105, 99, 104, 105, 101, 114, -62, -96,
                                    58])).decode(encoding="utf-8")),
    ("it-IT", bytearray(ints2bytes([78, 111, 116, 97, 58, 32, 102, 105, 108, 101, 32,
                                    105, 110, 99, 108, 117, 115, 111])).decode(encoding="utf-8")),
    ("ja-JP", bytearray(ints2bytes([-29, -125, -95, -29, -125, -94, 58, 32, -29, -126, -92, -29, -125, -77, -29, -126,
                                    -81, -29, -125, -85, -29, -125, -68, -29, -125, -119, 32, -29, -125, -107, -29,
                                    -126, -95, -29, -126, -92, -29, -125, -85, 58
                                    ])).decode(encoding="utf-8")),
    ("ko-KR", bytearray(ints2bytes([-20, -80, -72, -22, -77, -96, 58, 32, -19, -113, -84, -19, -107, -88, 32, -19,
                                    -116, -116, -20, -99, -68, 58])).decode(encoding="utf-8")),
    ("pl-PL", bytearray(ints2bytes([85, 119, 97, 103, 97, 58, 32, 119, 32, 116, 121, 109, 32, 112, 108, 105, 107, 117,
                                    58])).decode(encoding="utf-8")),
    ("pt-BR", bytearray(ints2bytes([79, 98, 115, 101, 114, 118, 97, -61, -89, -61, -93, 111, 58, 32, 105, 110, 99,
                                    108, 117, 105, 110, 100, 111, 32, 97, 114, 113, 117, 105, 118, 111, 58])).decode(encoding="utf-8")),
    ("ru-RU", bytearray(ints2bytes([-48, -97, -47, -128, -48, -72, -48, -68, -48, -75, -47, -121, -48, -80, -48, -67,
                                    -48, -72, -48, -75, 58, 32, -48, -78, -48, -70, -48, -69, -47, -114, -47, -121,
                                    -48, -75, -48, -67, -48, -72, -48, -75, 32, -47, -124, -48, -80, -48, -71, -48,
                                    -69, -48, -80, 58])).decode(encoding="utf-8")),
    ("tr-TR", bytearray(ints2bytes([78, 111, 116, 58, 32, 101, 107, 108, 101, 110, 101, 110, 32, 100, 111, 115, 121,
                                    97, 58])).decode(encoding="utf-8")),
    ("zh-CN", bytearray(ints2bytes([-26, -77, -88, -26, -124, -113, 58, 32, -27, -116, -123, -27, -112, -85, -26,
                                    -106, -121, -28, -69, -74, 58])).decode(encoding="utf-8")),
    ("es-ES", bytearray(ints2bytes([78, 111, 116, 97, 58, 32, 105, 110, 99, 108, 117, 115, 105, -61, -77, 110, 32,
                                    100, 101, 108, 32, 97, 114, 99, 104, 105, 118, 111, 58])).decode(encoding="utf-8"))
]


def printLangs():
    for lang in langList:
        langid, str = lang
        print(langid + ": " + str.encode("utf8"))
        # print(langid+str)
        # print(str)


def Main(src, dst):
    # `  408, 	"Note: including file: %s%s\n\x00"`
    msvc_prefix_regex = re.compile(r"(\s+408,\s+\")(.*)( %s%s\\n\\x00\"\s*\r\n)")
    rf = codecs.open(
        src, encoding="utf-16")
    found = False
    lines = []
    for line in rf:
        # print(type(line))
        # print(line)
        m = msvc_prefix_regex.match(line)
        if m is None:
            lines.append(line)
            continue
        head, str, tail = m.groups()
        # print(head, str, tail)
        for lang in langList:
            langid, prefixstr = lang
            # print(prefixstr.encode("gbk", "ignore"))
            # print(langid, prefixstr)
            if(str == prefixstr):
                found = True
                patchline = head + langList[0][1] + tail
                # print(patchline)
                lines.append(patchline)
                break
    if found is True:
        wf = codecs.open(dst, "w", encoding=rf.encoding)
        wf.write("".join(lines))
        wf.close()
    else:
        return "Can Not find msvc_deps_prefix in " + src

if __name__ == '__main__':
    sys.exit(Main(sys.argv[1], sys.argv[2]))
