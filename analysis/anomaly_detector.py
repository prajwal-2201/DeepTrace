import os

try:
    import magic
except ImportError:
    magic = None
    print("Warning: python-magic is not installed. File type mismatch detection will be limited.")

class AnomalyDetector:
    @staticmethod
    def detect_mismatch(file_path):
        """
        Compares the file extension against the true magic bytes of the file.
        Returns anomaly details if a mismatch is found.
        """
        if not os.path.exists(file_path):
            return None
            
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        
        # If no extension, we can't detect a mismatch, just report the true type
        if not ext:
            return None
            
        true_mime = "Unknown"
        true_type = "Unknown"
        is_anomaly = False
        
        if magic:
            try:
                # Use python-magic to get true mime and type
                m = magic.Magic(mime=True)
                true_mime = m.from_file(file_path)
                
                m_type = magic.Magic()
                true_type = m_type.from_file(file_path)
                
                # Basic mismatch logic
                if ext in ["jpg", "jpeg"] and "image/jpeg" not in true_mime:
                    is_anomaly = True
                elif ext == "png" and "image/png" not in true_mime:
                    is_anomaly = True
                elif ext == "pdf" and "application/pdf" not in true_mime:
                    is_anomaly = True
                elif ext in ["exe", "dll"] and "application/x-dosexec" not in true_mime:
                    is_anomaly = True
                elif ext == "txt" and "text/" not in true_mime:
                    is_anomaly = True
                    
            except Exception as e:
                print(f"Magic error on {file_path}: {e}")
                
        if is_anomaly:
            return {
                "file": file_path,
                "claimed_extension": ext,
                "true_mime": true_mime,
                "true_type": true_type,
                "severity": "HIGH",
                "reason": "File extension does not match magic bytes."
            }
            
        return None
