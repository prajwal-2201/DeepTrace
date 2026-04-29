import os

try:
    import pytsk3
except ImportError:
    pytsk3 = None

class FileRecoverer:
    def __init__(self, fs_info, output_dir="data/recovered"):
        self.fs_info = fs_info
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_file(self, fs_file, output_path):
        """Extracts the content of a pytsk3 FS_File to the disk."""
        if not fs_file.info.meta or fs_file.info.meta.size == 0:
            return False
            
        try:
            with open(output_path, "wb") as outfile:
                offset = 0
                size = fs_file.info.meta.size
                BUFF_SIZE = 1024 * 1024 # 1MB chunks
                
                while offset < size:
                    available_to_read = min(BUFF_SIZE, size - offset)
                    data = fs_file.read_random(offset, available_to_read)
                    if not data:
                        break
                    outfile.write(data)
                    offset += len(data)
            return True
        except Exception as e:
            print(f"Error extracting {output_path}: {e}")
            return False

    def recover_deleted_files(self, root_dir, current_path="/"):
        """Recursively walks the file system and extracts unallocated (deleted) files."""
        recovered_list = []
        if not pytsk3:
            return recovered_list

        for fs_object in root_dir:
            # Skip current and parent directory pointers
            if fs_object.info.name.name in [b".", b".."]:
                continue

            try:
                name = fs_object.info.name.name.decode('utf-8')
            except UnicodeDecodeError:
                name = fs_object.info.name.name.decode('latin-1', errors='replace')

            filepath = os.path.join(current_path, name)

            # Check if it's a directory
            if fs_object.info.meta and fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                try:
                    sub_directory = fs_object.as_directory()
                    # Recurse
                    recovered_list.extend(self.recover_deleted_files(sub_directory, filepath))
                except Exception as e:
                    pass
            
            # Check if it's a regular file
            elif fs_object.info.meta and fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
                # Is it unallocated (deleted)?
                if fs_object.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
                    # Sanitize filename
                    safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
                    if not safe_name:
                        safe_name = f"recovered_file_{fs_object.info.meta.addr}"
                        
                    output_path = os.path.join(self.output_dir, safe_name)
                    success = self.extract_file(fs_object, output_path)
                    
                    if success:
                        recovered_list.append({
                            "original_path": filepath,
                            "recovered_path": output_path,
                            "size": fs_object.info.meta.size
                        })

        return recovered_list
