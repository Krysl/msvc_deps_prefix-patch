# msvc_deps_prefix-patch

Patch `clui.dll` which is used by `cl.exe` to show the `Note: including file:`.  

All the `Note: including file:` in other languages will be changed to English version.  So, `Ninja` won't show tons of `Note: including file: XXXXXXXXXXXX` when build any more.

| Lang ID | Description                          | String template                          | BCP 47 Code |
| ------- | ------------------------------------ | ---------------------------------------- | ----------- |
| 1028    | Chinese - Taiwan                     | 注意: 包含檔案:%s%s\n                    | zh-TW       |
| 1029    | Czech                                | Poznámka: Včetně souboru:%s%s\n          | cs-CZ       |
| 1031    | German - Germany                     | Hinweis: Einlesen der Datei:%s%s\n       | de-DE       |
| 1033    | English - United States              | Note: including file:%s%s\n              | en-US       |
| 1036    | French - France                      | Remarque : inclusion du fichier : %s%s\n | fr-FR       |
| 1040    | Italian - Italy                      | Nota: file incluso %s%s\n                | it-IT       |
| 1041    | Japanese                             | メモ: インクルード ファイル: %s%s\n      | ja-JP       |
| 1042    | Korean                               | 참고: 포함 파일:%s%s\n                   | ko-KR       |
| 1045    | Polish                               | Uwaga: w tym pliku: %s%s\n               | pl-PL       |
| 1046    | Portuguese - Brazil                  | Observação: incluindo arquivo:%s%s\n     | pt-BR       |
| 1049    | Russian                              | Примечание: включение файла: %s%s\n      | ru-RU       |
| 1055    | Turkish                              | Not: eklenen dosya: %s%s\n               | tr-TR       |
| 2052    | Chinese - People's Republic of China | 注意: 包含文件: %s%s\n                   | zh-CN       |
| 3082    | Spanish - Spain (Modern Sort)        | Nota: inclusión del archivo:%s%s\n       | es-ES       |

![](./doc/clui.dll%20change.png)


## How to Use?

1. `git clone --depth=1 https://github.com/Krysl/msvc_deps_prefix-patch.git`
2. `cd msvc_deps_prefix-patch`
3. Install the needed tools
   - Necessary
     - Assuming you already have
       - Git
       - wget
       - python 2.7
       - [Ninja](https://ninja-build.org/)
     - To be download/install in `.\tools` folder
       - [Resource Hacker](http://www.angusj.com/resourcehacker)
   - Optional
     - [gsudo](https://github.com/gerardog/gsudo)
  Just run the `.\scripts\download_tools.bat`

3. Generate the template setting file `template.json`
   ```
   Usage: configure.py [options]

   Options:
     -h, --help            show this help message and exit
     -f FILE, --file=FILE  where to save the config file. (default "template.json")
     -S, --showExcludes    enable to show the paths that have been filtered by the filtering options. (default not)
     -H HOST, --host=HOST  host filter, can be x64,x86 . if not set, all host been accepted
     -T TARGET, --target=TARGET
                           target filter, can be x64,x86 . if not set, all target been accepted
     -L LANG, --lang=LANG  Lang ID filter, it's a number, see the README.md about "Lang ID" . if not set, all lang beenaccepted     
     -d, --debug
   ```
   for example:
   - `Host x64`, `chinese`, `show filtered`
     - `python configure.py -Hx64 -L 2052 -S`
       - this will output the `template.json`:  
         in `switch`, set to `false` to disable all in that folder;  
         in `filters`, you can add more filters to filter paths in `clui_list`;  
         in `custom_list`, you can add Absolute paths of 'clui.dll' to be patch;    
        ```json
        {
            "remark": {
                "cmd": "configure.py -Hx64 -L 2052 -S"
            },
            "switch": {
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools": true,
                "D:\\Program Files\\Microsoft Visual Studio\\2019\\Community": true
            },
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools": {
                "root_path": "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools",
                "filters": {
                    "lang": [
                        2052
                    ],
                    "host": [
                        "x64"
                    ],
                    "target": []
                },
                "clui_list": [
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\Hostx64\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\Hostx64\\x86\\2052\\clui.dll"
                ],
                "clui_list_excludes": [
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\Hostx86\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\Hostx86\\x86\\2052\\clui.dll"
                ]
            },
            "D:\\Program Files\\Microsoft Visual Studio\\2019\\Community": {
                "root_path": "D:\\Program Files\\Microsoft Visual Studio\\2019\\Community",
                "filters": {
                    "lang": [
                        2052
                    ],
                    "host": [
                        "x64"
                    ],
                    "target": []
                },
                "clui_list": [
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX64\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX64\\x86\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx64\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx64\\x86\\2052\\clui.dll"
                ],
                "clui_list_excludes": [
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX64\\x64\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX64\\x86\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX86\\x64\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX86\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX86\\x86\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.16.27023\\bin\\HostX86\\x86\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx64\\x64\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx64\\x86\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx86\\x64\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx86\\x64\\2052\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx86\\x86\\1033\\clui.dll",
                    "VC\\Tools\\MSVC\\14.29.30037\\bin\\Hostx86\\x86\\2052\\clui.dll"
                ]
            },
            "custom_list": []
        }
        ```

4. rename `template.json` to `config.json`  
  `mv template.json config.json`

5. generate the ninja project  
   run `python gen_ninja.py`, and there will be a ninja project in `.\out` folder  

6. build the ninja project to generate patched dll  
   `ninja -C out`
7. install the patched dll  
   `install.bat`, `admin_install.bat` will be generated
   it's a simple script to copy patched dll to the original place, run one of them to install
   

## TODO
- simplify usage
- add the feature of recovering dll
  - for now, it's backup in out folder
    - Original dll: out\41f810c1721f6a7ffa9bd0670dcab9e1\clui.original.dll
    - find original path: out\41f810c1721f6a7ffa9bd0670dcab9e1\clui.modified.ver.rc

Probably no one but me will use this project.
They can use [Resource Hacker](http://www.angusj.com/resourcehacker) to modify the `clui.dll` manually, even simpler than using this project.  
This is my first python project with more than 50 lines.  
Need a lot of refactoring and optimization.