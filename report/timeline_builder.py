class TimelineBuilder:
    @staticmethod
    def build_timeline(metadata_list):
        """
        Takes a list of file metadata and builds a chronological timeline.
        Each file generates multiple events (Created, Modified, Accessed).
        """
        events = []
        
        for meta in metadata_list:
            filepath = meta.get("file_path", "Unknown")
            
            # Map MAC times to events
            times = [
                (meta.get("created"), "Created"),
                (meta.get("modified"), "Modified"),
                (meta.get("accessed"), "Accessed")
            ]
            
            for timestamp, action in times:
                if timestamp and timestamp != "N/A" and timestamp != "Invalid Timestamp":
                    events.append({
                        "timestamp": timestamp,
                        "action": action,
                        "file": filepath,
                        "deleted": meta.get("deleted", False)
                    })
                    
        # Sort events chronologically
        # The timestamp string is 'YYYY-MM-DD HH:MM:SS UTC', so basic string sorting works
        sorted_events = sorted(events, key=lambda x: x["timestamp"])
        
        return sorted_events
