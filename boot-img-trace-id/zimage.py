import os
import subprocess

_GZIP_MAGIC = b'\x1f\x8b\x08\x00'
_TRACE_PID = bytearray("TracerPid:\t%d", "utf-8")

class ZImage():
    def __init__(self, path):
        super().__init__()
        self.path = path
        self._check_exists()
        self.root_folder = os.path.dirname(self.path)
        self.patched_path = self._path("zImage_patched")
        self.body_ungz_path = self._path("zImage_body")
        self.body_path = self._path("zImage_body.gz")
        self.body_patched_ungz_path = self._path("zImage_body_patched")
        self.body_patched_path = self._path("zImage_body_patched.gz")

    def _path(self, prefix: str) -> str:
        return os.path.join(self.root_folder, f"boot.img-{prefix}")

    def _extra_body(self):
        with open(self.body_path, 'wb') as f:
            f.write(self.body_content)
        subprocess.run(['gunzip', self.body_path]) 
        with open(self.body_ungz_path, 'r+b') as f:
            self.body_ungz_content = f.read()

    def _replace_trace_id(self) -> bytearray:
        global _TRACE_PID
        self._extra_body()
        index = self.body_ungz_content.find(_TRACE_PID)
        assert index > 0, f"BootImgProcessor can't find trace pid in image"
        content_patched = self.body_ungz_content.replace(_TRACE_PID, bytearray("TracerPid:\t00", "utf-8"))
        assert content_patched.find(_TRACE_PID) < 0, "why after repalce, can still find??"
        return content_patched

    def _patch(self):
        content_patched = self._replace_trace_id()
        assert len(content_patched) > 0
        with open(self.body_patched_ungz_path, "w+b") as f:
            f.write(content_patched)
        assert os.path.exists(self.body_patched_ungz_path)
        gzip_param = ['-n','-9', '-v', self.body_patched_ungz_path]
        print("gzip param: " + " ".join(gzip_param))
        subprocess.run(['gzip'] + gzip_param)

        assert os.path.exists(self.body_patched_path)
        with open(self.body_patched_path, "r+b") as f:
            body_patchd_content = f.read()
        assert len(body_patchd_content) > 0

        patched_content = self.content[0: self.gz_index] + body_patchd_content + self.content[self.gz_index + len(body_patchd_content):]
        assert len(patched_content) == len(self.content)
        with open(self.patched_path, "w+b") as f:
            f.write(patched_content)

    def process(self):
        """
        create the image_patched
        """
        global _GZIP_MAGIC
        self.content = open(self.path, 'r+b').read()
        self.gz_index = self.content.find(_GZIP_MAGIC)
        assert self.gz_index > 0
        self.body_content = self.content[self.gz_index: ]
        self._patch()


    def _check_exists(self):
        if not os.path.exists(self.path):
            sys.exit("ZImage path not exist: " + self.img_path)