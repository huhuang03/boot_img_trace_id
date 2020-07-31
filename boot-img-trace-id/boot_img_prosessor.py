import subprocess

class BootImgProcessor:
    def __init__(self):
        super().__init__()
        self.img_path = ""

    def process(self, img_path):
        self.img_path = img_path
        self._check_exists()
        subprocess.run([""])



    def _check_exists(self):
        if not os.path.exists(self.path):
            sys.exit("Kernel path not exist: " + self.path)