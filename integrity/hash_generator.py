import hashlib
import os

class HashGenerator:
    @staticmethod
    def generate_hashes(file_path):
        """Generates MD5 and SHA256 hashes for a given file."""
        if not os.path.exists(file_path):
            return None
            
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
                    
            return {
                "file": file_path,
                "md5": md5_hash.hexdigest(),
                "sha256": sha256_hash.hexdigest()
            }
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None
