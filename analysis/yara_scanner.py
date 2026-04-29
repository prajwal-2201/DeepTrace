import os

try:
    import yara
except ImportError:
    yara = None
    print("Warning: yara-python not installed. Threat scanning will be skipped.")

class YaraScanner:
    def __init__(self, rules_dir="data/rules"):
        self.rules_dir = rules_dir
        self.rules = None
        self._load_rules()

    def _load_rules(self):
        if not yara:
            return
            
        rule_files = {}
        if os.path.exists(self.rules_dir):
            for filename in os.listdir(self.rules_dir):
                if filename.endswith(".yar") or filename.endswith(".yara"):
                    filepath = os.path.join(self.rules_dir, filename)
                    rule_files[filename] = filepath
                    
        if rule_files:
            try:
                self.rules = yara.compile(filepaths=rule_files)
            except Exception as e:
                print(f"Error compiling YARA rules: {e}")

    def scan_file(self, file_path):
        """Scans a single file against the compiled YARA rules."""
        if not self.rules or not os.path.exists(file_path):
            return []
            
        try:
            matches = self.rules.match(file_path)
            findings = []
            for match in matches:
                findings.append({
                    "file": file_path,
                    "severity": match.meta.get("severity", "High"),
                    "rule_name": match.rule,
                    "description": match.meta.get("description", "No description"),
                    "reason": "YARA Signature Match"
                })
            return findings
        except Exception as e:
            print(f"YARA scan error on {file_path}: {e}")
            return []
