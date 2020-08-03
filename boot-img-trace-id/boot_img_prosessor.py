import subprocess
import os
from pathlib import Path
from tool.tool import *
from zimage import ZImage

_TRACE_PID = bytearray("TracerPid:\t%d", "utf-8")
_GZIP_MAGIC = b'\x1f\x8b\x08\x00'

class BootImgProcessor:
    OUTPUT_FOLDER = "out"

    def __init__(self):
        super().__init__()
        self.img_path = ""
        self.zimage_content = None
        self.zimage_content_patched = None
        self.gz_index = 0

    def _path(self, subprefix: str) -> str:
        return os.path.join(self.OUTPUT_FOLDER, f"boot.img-{subprefix}")

    def _read(self, subprefix: str) -> str:
        return open(self._path(subprefix)).read().replace('\n', '')

    def _fill_zero(self):
        patched_size = os.path.getsize(self.img_patched_path)
        if patched_size > self.img_size:
            raise "Why patched size > img size"

        if patched_size < self.img_size:
            fill_size = self.img_size - patched_size
            fill_content = bytearray(fill_size)
            with open(self.img_patched_path, 'a+b') as f:
                f.write(fill_content)
            print("origin file md5: ", self.img_md5)
            print("after patched file md5: ", md5(self.img_patched_path))

    def _pack(self):
        param = ["--kernel", self.zimage_patched_path, "--ramdisk", self.ramdisk_path, "--cmdline", f"{self.cmdline}", "--base", self.base, '--pagesize', self.pagesize, "--ramdisk_offset", self.ramdisk_offset, "--tags_offset", self.tags_offset]
        param += ['-o', self.img_patched_path]
        print("pack param: ", " ".join(param))
        subprocess.run(["mkbootimg"] + param)

    def process(self, img_path):
        self.img_path = img_path
        self._check_exists()
        self.img_size = os.path.getsize(self.img_path)
        self.img_md5 = md5(self.img_path)
        Path(self.OUTPUT_FOLDER).mkdir(exist_ok=True)
        subprocess.run(["unpackbootimg", "-i", self.img_path, "-o", self.OUTPUT_FOLDER])

        self.img_patched_path = "boot_patched.img"
        self.kernel_gzip_path = self._path("kernelimage.gz")
        self.zimage_patched_path = self._path("zImage_patched")
        self.zimage_content = open(self._path('zImage'), 'r+b').read()
        self.zimage_sub_path = self._path('zImage_sub')
        self.zimage_sub_gz_path = self.zimage_sub_path + ".gz"
        self.cmdline = self._read("cmdline")
        self.base = self._read('base')
        self.pagesize = self._read('pagesize')
        self.zimage_path = self._path("zImage")
        self.ramdisk_path = self._path("ramdisk.gz")
        self.ramdisk_offset = self._read("ramdisk_offset")
        self.tags_offset = self._read('tags_offset')

        ZImage(self.zimage_path).process()
        self._pack()
        self._fill_zero()

    def _check_exists(self):
        if not os.path.exists(self.img_path):
            sys.exit("Kernel path not exist: " + self.img_path)