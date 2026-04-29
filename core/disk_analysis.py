import os
import sys

# Attempt to import forensics libraries gracefully
try:
    import pytsk3
except ImportError:
    pytsk3 = None
    print("Warning: pytsk3 is not installed. Disk parsing will be mocked or fail.")

try:
    import pyewf
except ImportError:
    pyewf = None
    print("Warning: pyewf is not installed. E01 image support will be limited.")

class EWFImgInfo(pytsk3.Img_Info if pytsk3 else object):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()


class DiskAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_info = None
        self.fs_info = None
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

    def load_image(self):
        if not pytsk3:
            raise Exception("pytsk3 is required but not installed.")
            
        # Detect if E01 or RAW
        if self.image_path.lower().endswith('.e01'):
            if not pyewf:
                raise Exception("pyewf is required for E01 support but not installed.")
            
            filenames = pyewf.glob(self.image_path)
            ewf_handle = pyewf.handle()
            ewf_handle.open(filenames)
            self.img_info = EWFImgInfo(ewf_handle)
        else:
            # Assuming RAW/DD image
            self.img_info = pytsk3.Img_Info(self.image_path)

        # Attempt to open file system
        try:
            self.fs_info = pytsk3.FS_Info(self.img_info)
        except IOError as e:
            # Might be a partition table instead of raw FS
            try:
                vol_mgr = pytsk3.Volume_Info(self.img_info)
                # Just take the first partition for this demo, in a real tool we iterate
                for part in vol_mgr:
                    if part.flags == pytsk3.TSK_VS_PART_FLAG_ALLOC:
                        try:
                            self.fs_info = pytsk3.FS_Info(self.img_info, offset=part.start * vol_mgr.info.block_size)
                            break
                        except:
                            continue
            except IOError:
                raise Exception("Could not find a valid file system or volume system.")

        if not self.fs_info:
            raise Exception("Failed to open file system.")
        
        return True

    def get_root_directory(self):
        if not self.fs_info:
            raise Exception("File system not loaded.")
        return self.fs_info.open_dir(path="/")
