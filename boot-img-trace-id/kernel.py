import os
import sys
import subprocess

_GZIP_MAGIC = b'\x1f\x8b\x08\x00'

_TRACE_PID = bytearray("TracerPid:\t%d", "utf-8")

class Kernel:
    def __init__(self, path):
        super().__init__()
        self.path = os.path.abspath(path)
        self._check_exists()
        self.img_path = os.path.join(os.path.dirname(self.path), 'kernelimage')
        self.content = None
        self.content_gz_magic_index = 0

    def process(self):
        self.img_content = open(self.img_path, 'r+b').read()
        assert self.img_content.find(_TRACE_PID) > 0, "can't find tracePid in kernelimage"
        img_content_patched = self.img_content.replace(_TRACE_PID, bytearray("TracerPid:\t00", "utf-8"))
        assert img_content_patched.find(_TRACE_PID) < 0, "why after repalce, can still find??"
        open(self.img_path + "_patched", 'w+b').write(img_content_patched)
        subprocess.run(["gzip", "-n", "-f", "-9", self.img_path + "_patched"])

    
    def extra_kernel_manually(self, new_file_name="img_by_sub_gzip") -> str:
        global _GZIP_MAGIC
        """
        manually extra kenel(find gizp part, and then extra)
        [new_file_name]: the output filename
        [return]: the output file
        """
        self.get_content()
        gzip_magic_index = self.content.find(_GZIP_MAGIC)
        if gzip_magic_index <= 0:
            sys.exit("Kernel extra_kernel_manually can't find gzip in kenrl file: ", self.path)
        gzip_content = self.content[gzip_magic_index: ]
        out_path = os.path.join(os.path.dirname(self.path), os.path.basename(self.path) + new_file_name)
        gzip_path = out_path + ".gz"
        open(gzip_path, 'w+b').write(gzip_content)
        subprocess.run(["gunzip", gzip_path])

    def get_content(self):
        if self.content is None:
            self.content = open(self.path, 'rb').read()
            self.content_gz_magic_index = self.content.find(_GZIP_MAGIC)
            if gzip_magic_index <= 0:
                sys.exit("Kernel get kernel content can't find gzip in kernel file: ", self.path)
        return self.content

    def _check_exists(self):
        if not os.path.exists(self.path):
            sys.exit("Kernel path not exist: " + self.path)