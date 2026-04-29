from PIL import Image
import numpy as np

class LSBDetector:
    @staticmethod
    def extract_lsbs(image_path, num_bits=1000):
        """Extracts the LSBs from the first few pixels of an image."""
        try:
            img = Image.open(image_path)
            # Ensure RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            pixels = np.array(img).flatten()
            
            # Extract LSB of each color channel
            lsbs = pixels & 1
            
            # Pack bits into bytes
            bytes_data = np.packbits(lsbs)
            
            # Return the first few bytes as hex for inspection
            return bytes_data.tobytes()
        except Exception as e:
            return None

    @staticmethod
    def detect_hidden_data(image_path):
        """
        A heuristic to detect hidden data by looking at the entropy of the LSB plane.
        If LSBs are purely noise (high entropy), it might contain encrypted/compressed hidden data.
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pixels = np.array(img).flatten()
            lsbs = pixels & 1
            
            # Calculate entropy of LSBs
            p1 = np.sum(lsbs) / len(lsbs)
            p0 = 1 - p1
            
            if p1 == 0 or p0 == 0:
                entropy = 0
            else:
                entropy = - (p0 * np.log2(p0) + p1 * np.log2(p1))
                
            # If entropy is extremely close to 1.0, the LSBs are perfectly random (suspicious)
            is_suspicious = entropy > 0.99
            
            return {
                "file": image_path,
                "lsb_entropy": round(entropy, 4),
                "suspicious": bool(is_suspicious)
            }
        except Exception as e:
            return {"error": str(e)}
