import os

_GZIP_MAGIC = b'\x1f\x8b\x08\x00'

class ZImage():
    def __init__(self, path):
        super().__init__()
        self.path = path

    def _path(self, prefix: str) -> str:
        return f"boot.img-{prefix}"

    def process(self):
        """
        create the image_patched
        """
        self.content = open(self.path).read()
        # self.gz_index = 


    def _check_exists(self):
        if not os.path.exists(self.path):
            sys.exit("ZImage path not exist: " + self.img_path)