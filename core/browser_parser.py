import os
import sqlite3

class BrowserParser:
    @staticmethod
    def parse_chrome_history(db_path):
        """Extracts URLs and visit times from Chrome/Edge History SQLite DB."""
        if not os.path.exists(db_path):
            return None
            
        try:
            # Connect in read-only mode to prevent locking/modifying evidence
            uri = f"file:{db_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            cursor = conn.cursor()
            
            query = """
            SELECT url, title, visit_count, 
            datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime') as last_visited
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 50;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "url": row[0],
                    "title": row[1],
                    "visits": row[2],
                    "last_visited": row[3]
                })
                
            return {"browser": "Chrome/Edge", "history": history}
        except Exception as e:
            print(f"Error parsing browser DB {db_path}: {e}")
            return None
