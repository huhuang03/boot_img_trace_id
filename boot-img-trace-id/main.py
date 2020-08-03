import os
import sys
from pathlib import Path
import subprocess
import shutil
import re
import kernel
from kernel import Kernel
from boot_img_prosessor import BootImgProcessor

_BOOT_EXTRA_FOLDER = "extracted"


_TRACE_PID = bytearray("TracerPid:\t%d", "utf-8")

PACK_FOLDER = "pack"

_KERNEL_PATCHED = "kernelimage_patched"

def _find_pos(content, to_find_bytearray):
    return content.find(to_find_bytearray)

def _get_kernel_image_content_handly():
    kernel_path = "kernel"
    kernel_content = open(kernel_path, 'rb').read()
    header_index = _find_pos(kernel_content, _GZIP_MAGIC)
    if header_index <= 0:
        print("cna't find gzip magic in pos")
        return

    kernel_content_gzip = kernel_content[header_index: ]

    kernel_content_ungzip = ungzip(kernel_content_gzip)
    # are you sure thant can simpley change `TraceId`??


def _get_kernel_image_content():
    # If you not use imjtool. you must do unzip yourself
    return open('kernelimage', 'rb').read()

def extra_kernel_manually(kernel_path, new_file_name="img_by_ungzip") -> str:
    kernel_path = path.abspath(kernel_path)
    if not os.path.exist(kernel_path):
        sys.exit("extra_kernel_manually input kernel path not exists: " + kernel_path)
    
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

    processor = BootImgProcessor()
    processor.process(boot_img_path)

    # subprocess.run(["imjtool.MacOS", boot_img_path, "extract"])
    # # shutil.copytree(_BOOT_EXTRA_FOLDER, PACK_FOLDER)

    # os.chdir(_BOOT_EXTRA_FOLDER)
    # kernel = Kernel("kernel")
    # kernel.process()
    # kernel_image_content = _get_kernel_image_content()
    # tracePid_index = _find_pos(kernel_image_content, _TRACE_PID)
    # if tracePid_index <=0:
    #     print("can't find tracePid in kernelimage")
    #     return
    # print("tracePid index: ", tracePid_index)

    # kernel_image_content = kernel_image_content.replace(_TRACE_PID, bytearray("TracerPid:\t00", "utf-8"))
    # assert _find_pos(kernel_image_content, _TRACE_PID) < 0, "Why after repalce, can still find??"
    # # write to modfied
    # open(_KERNEL_PATCHED, 'wb').write(kernel_image_content)

    # imgs = [_KERNEL_PATCHED, "ramdisk", "kernel", "devicetree.dtb"] 
    # make_param = ["make", "boot_patched.img"] + imgs
    # subprocess.run(["imjtool.MacOS"] + make_param)

    # kernel_content[header_index:] = kernel_modified_gziped

    # write_kernel_content_to_pack_folder()
    # pack_to_pakc_folder()

if __name__ == "__main__":
    main()