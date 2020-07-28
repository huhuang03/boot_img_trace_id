import os
import sys
from pathlib import Path
import subprocess
import shutil

_BOOT_EXTRA_FOLDER = "extracted"

_GZIP_MAGIC = b'\x1f\x8b\x08\x00'

_TRACE_PID = bytearray("TracerPid:\\t%d", "utf-8")

PACK_FOLDER = "pack"

def _find_pos(content, to_find_bytearray):
    return -1

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} boot_img_path")
        return

    boot_img_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(boot_img_path):
        print(f"{boot_img_path} not exist")
        return

    # yes, you must have imjtool to extra the boot_img_path
    Path('runtime').mkdir(exist_ok=True)
    os.chdir("runtime")
    shutil.rmtree(_BOOT_EXTRA_FOLDER, ignore_errors=True)
    shutil.rmtree(PACK_FOLDER, ignore_errors=True)

    subprocess.run(["imjtool.MacOS", boot_img_path, "extract"])
    shutil.copytree(_BOOT_EXTRA_FOLDER, PACK_FOLDER)

    os.chdir(_BOOT_EXTRA_FOLDER)
    kernel_path = "kernel"
    kernel_content = open(kernel_path, 'rb').read()
    header_index = _find_pos(kernel_content, _GZIP_MAGIC)
    if header_index <= 0:
        print("cna't find gzip magic in pos")
        return

    kernel_content_gzip = kernel_content[header_index: ]

    kernel_content_ungzip = ungzip(kernel_content_gzip)
    # are you sure thant can simpley change `TraceId`??
    tracePid_index = _find_pos(kernel_content_ungzip, _TRACE_PID)
    if tracePid_index <=0:
        print("can't find tracePid index in gzip unziped")
        return

    kernel_content_ungzip[tracePid_index: tracePid_index + len(_TRACE_PID)] = bytearray("TracerPid:\\t00")
    kernel_modified_gziped = gzip(kernel_content_ungzip)

    kernel_content[header_index:] = kernel_modified_gziped

    write_kernel_content_to_pack_folder()
    pack_to_pakc_folder()
    

if __name__ == "__main__":
    main()