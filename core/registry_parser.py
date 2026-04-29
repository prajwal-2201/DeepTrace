import os

try:
    from regipy.registry import RegistryHive
except ImportError:
    RegistryHive = None
    print("Warning: regipy not installed. Registry parsing will be skipped.")

class RegistryParser:
    @staticmethod
    def parse_hive(hive_path):
        """
        Parses a Windows Registry Hive (SAM, SYSTEM, NTUSER.DAT)
        to extract useful forensic artifacts.
        """
        if not RegistryHive or not os.path.exists(hive_path):
            return None
            
        hive_name = os.path.basename(hive_path).upper()
        results = {"hive": hive_name, "artifacts": []}
        
        try:
            hive = RegistryHive(hive_path)
            
            # Very basic extraction depending on the hive
            if "SAM" in hive_name:
                # Typically we'd parse SAM for users, but regipy has plugins for this.
                # For demonstration, we'll just check if the hive opens.
                results["artifacts"].append("SAM Hive loaded successfully.")
                
            elif "SYSTEM" in hive_name:
                # Parse USB devices
                try:
                    usb_key = hive.get_key(r'ControlSet001\Enum\USBSTOR')
                    usb_devices = [sub.name for sub in usb_key.iter_subkeys()]
                    results["artifacts"].append(f"Found {len(usb_devices)} connected USB devices.")
                except Exception:
                    pass
                    
            elif "NTUSER.DAT" in hive_name:
                # Parse RecentDocs
                try:
                    recent_key = hive.get_key(r'Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs')
                    recent_files = [val.name for val in recent_key.iter_values()]
                    results["artifacts"].append(f"Found {len(recent_files)} recent documents.")
                except Exception:
                    pass

            return results
        except Exception as e:
            print(f"Error parsing registry hive {hive_path}: {e}")
            return None
