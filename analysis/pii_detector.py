import re
import os

class PIIDetector:
    # Basic Regex patterns for demonstration
    PATTERNS = {
        "Email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        "CreditCard": r'\b(?:\d[ -]*?){13,16}\b',
        "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
        "BitcoinAddress": r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
    }

    @staticmethod
    def scan_file(file_path):
        """Scans a text file for exposed PII data."""
        if not os.path.exists(file_path):
            return []
            
        # Only scan files under 5MB to avoid memory issues on huge binaries
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            return []
            
        findings = []
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                
            for pii_type, pattern in PIIDetector.PATTERNS.items():
                matches = set(re.findall(pattern, content))
                for match in matches:
                    # Basic validation to reduce false positives
                    if pii_type == "CreditCard":
                        clean_cc = re.sub(r'[- ]', '', match)
                        if len(clean_cc) < 13 or len(clean_cc) > 16:
                            continue
                            
                    findings.append({
                        "file": file_path,
                        "type": "PII_LEAK",
                        "severity": "High",
                        "reason": f"Found {pii_type}",
                        "preview": match[:4] + "****" + match[-4:] if len(match)>8 else "****"
                    })
        except Exception as e:
            print(f"PII scan error on {file_path}: {e}")
            
        return findings
