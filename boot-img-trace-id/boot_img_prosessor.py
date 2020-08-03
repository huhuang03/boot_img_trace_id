import subprocess
import os
from pathlib import Path
from tool.tool import *

_TRACE_PID = bytearray("TracerPid:\t%d", "utf-8")
_GZIP_MAGIC = b'\x1f\x8b\x08\x00'

class BootImgProcessor:
    OUTPUT_FOLDER = "out"

    def __init__(self):
        super().__init__()
        self.img_path = ""
        self.zimage_content = None
        self.zimage_content_patched = None

    def _replace_trace_id(self, content: bytearray) -> bytearray:
        global _GZIP_MAGIC
        gzip_index = content.find(_GZIP_MAGIC)
        print("gzip index: ", gzip_index)
        index = content.find(_TRACE_PID)
        assert index > 0, f"BootImgProcessor can't find trace pid in image"
        content_patched = content.replace(_TRACE_PID, bytearray("TracerPid:\t00", "utf-8"))
        assert content_patched.find(_TRACE_PID) < 0, "why after repalce, can still find??"
        return content_patched

    def _path(self, subprefix: str) -> str:
        return os.path.join(self.OUTPUT_FOLDER, f"boot.img-{subprefix}")

    def _read(self, subprefix: str) -> str:
        return open(self._path(subprefix)).read().replace('\n', '')

    def _fill_zero():
        self.pathed_size = os.path.getsize(self.img_patched_path)
        
        # pass

    def _pack(self):
        param = ["--kernel", self.kernel_path, "--ramdisk", self.ramdisk_path, "--cmdline", f"'{self.cmdline}'", "--base", self.base, '--pagesize', self.pagesize, "--ramdisk_offset", self.ramdisk_offset]
        param += ['-o', self.img_patched_path]
        print("pack param: ", " ".join(param))
        subprocess.run(["mkbootimg"] + param)

    def process(self, img_path):
        self.img_path = img_path
        self._check_exists()
        self.img_size = os.path().getsize(self.img_path)
        self.img_md5 = md5(self.img_path)
        Path(self.OUTPUT_FOLDER).mkdir(exist_ok=True)
        subprocess.run(["unpackbootimg", "-i", self.img_path, "-o", self.OUTPUT_FOLDER])
        self.cmdline = self._read("cmdline")
        self.base = self._read('base')
        self.pagesize = self._read('pagesize')
        self.zimage_content = open(os.path.join(self.OUTPUT_FOLDER, "boot.img-zImage"), 'r+b').read()
        self.kernel_path = self._path("zImage")
        self.ramdisk_path = self._path("ramdisk.gz")
        self.ramdisk_offset = self._read("ramdisk_offset")
        self.img_patched_path = "boot_patched.img"
        # self.zimage_content_patched = self._replace_trace_id(self.zimage_content)
        # print(len(self.zimage_content_patched))
        self._pack()

    def _check_exists(self):
        if not os.path.exists(self.img_path):
            sys.exit("Kernel path not exist: " + self.img_path)