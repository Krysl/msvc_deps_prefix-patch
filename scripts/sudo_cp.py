import os
import shutil
import sys
import win32con
from win32runas import is_admin, runas


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def Main(src, dst, stamp, timefile=None):
    print(src, dst, stamp, timefile)
    if is_admin():
        # print("run as admin")
        # Use copy instead of copyfile to ensure the executable bit is copied.
        dstpath = os.path.normpath(dst)
        rc = None
        if timefile is not None:
            tmpfile = stamp+".time"
            touch(tmpfile)
            shutil.copystat(os.path.normpath((timefile)), tmpfile)
            rc = shutil.copy(src, dstpath)
            shutil.copystat(tmpfile, dstpath)
            os.remove(tmpfile)
        else:
            rc = shutil.copy(src, dstpath)
        touch(stamp)
        return rc
    else:
        # Re-run the program with admin rights
        cmd = '"%s"' % sys.executable
        params = " ".join(['"%s"' % (x,) for x in sys.argv])

        print("runas Administrator", cmd, params)
        rc = runas(executable=cmd, args=params,
                   nShow=win32con.SW_SHOWNORMAL, waitClose=True)

        if rc is True:
            # touch(stamp)
            return None
        else:
            # touch(stamp + ".err")
            return -rc


if __name__ == '__main__':
    sys.exit(Main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
