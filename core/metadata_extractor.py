from datetime import datetime

try:
    import pytsk3
except ImportError:
    pytsk3 = None

class MetadataExtractor:
    @staticmethod
    def extract_metadata(fs_object, filepath):
        """Extracts MAC timestamps and file attributes from a pytsk3 FS_Object."""
        if not pytsk3 or not fs_object.info.meta:
            return None

        meta = fs_object.info.meta
        
        # Convert timestamp to human readable format
        def ts_to_str(ts):
            if ts == 0:
                return "N/A"
            try:
                return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S UTC')
            except Exception:
                return "Invalid Timestamp"

        metadata = {
            "file_path": filepath,
            "inode_addr": meta.addr,
            "type": "Directory" if meta.type == pytsk3.TSK_FS_META_TYPE_DIR else "File",
            "size": meta.size,
            "created": ts_to_str(meta.crtime) if hasattr(meta, 'crtime') else "N/A",
            "modified": ts_to_str(meta.mtime),
            "accessed": ts_to_str(meta.atime),
            "changed": ts_to_str(meta.ctime), # MFT modified
            "deleted": bool(meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC)
        }
        
        return metadata

    @staticmethod
    def walk_and_extract(root_dir, current_path="/"):
        """Recursively walks the FS and returns a list of metadata for all files."""
        all_metadata = []
        if not pytsk3:
            return all_metadata

        for fs_object in root_dir:
            if fs_object.info.name.name in [b".", b".."]:
                continue

            try:
                name = fs_object.info.name.name.decode('utf-8')
            except UnicodeDecodeError:
                name = fs_object.info.name.name.decode('latin-1', errors='replace')

            filepath = f"{current_path.rstrip('/')}/{name}"
            
            meta = MetadataExtractor.extract_metadata(fs_object, filepath)
            if meta:
                all_metadata.append(meta)

            if fs_object.info.meta and fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                try:
                    sub_directory = fs_object.as_directory()
                    all_metadata.extend(MetadataExtractor.walk_and_extract(sub_directory, filepath))
                except Exception:
                    pass

        return all_metadata
