import math
import os

class EntropyChecker:
    @staticmethod
    def calculate_entropy(file_path):
        """
        Calculates the Shannon entropy of a file.
        Returns a float between 0.0 and 8.0.
        Files with entropy > 7.5 are likely compressed or encrypted.
        """
        if not os.path.exists(file_path):
            return 0.0
            
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            if not data:
                return 0.0
                
            entropy = 0
            # Calculate byte frequencies
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
                
            length = len(data)
            for count in byte_counts:
                if count > 0:
                    p = count / length
                    entropy -= p * math.log2(p)
                    
            return float(entropy)
        except Exception as e:
            print(f"Error calculating entropy for {file_path}: {e}")
            return 0.0

    @staticmethod
    def analyze_file(file_path):
        entropy = EntropyChecker.calculate_entropy(file_path)
        is_suspicious = entropy > 7.85 # High threshold for encryption/packing
        
        return {
            "file": file_path,
            "entropy": round(entropy, 4),
            "is_encrypted_or_packed": is_suspicious
        }
