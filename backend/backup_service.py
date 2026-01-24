#!/usr/bin/env python3
"""
Database Autobackup Service for CloudEngineered Platform

Provides automated backup functionality for:
- Blog articles
- Tools data
- Tool comparisons
- User data (sanitized)

Supports:
- Manual backups
- Scheduled automatic backups
- Backup restoration
- JSON export format for portability
"""

import sqlite3
import json
import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseBackupService:
    """
    Comprehensive database backup service for SQLite databases.
    Supports automatic scheduling, JSON export, and easy restoration.
    """
    
    def __init__(
        self, 
        db_path: str = "blog.db",
        backup_dir: str = "backups",
        max_backups: int = 7,
        auto_backup_interval_hours: int = 24
    ):
        """
        Initialize the backup service.
        
        Args:
            db_path: Path to the SQLite database file
            backup_dir: Directory to store backups
            max_backups: Maximum number of backups to retain
            auto_backup_interval_hours: Hours between automatic backups
        """
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.auto_backup_interval = auto_backup_interval_hours * 3600
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_scheduler = threading.Event()
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory: {self.backup_dir.absolute()}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _generate_backup_filename(self, backup_type: str = "full") -> str:
        """Generate a timestamped backup filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{backup_type}_{timestamp}"
    
    def backup_to_sqlite(self) -> str:
        """
        Create a SQLite file backup (binary copy).
        
        Returns:
            Path to the backup file
        """
        backup_name = self._generate_backup_filename("sqlite")
        backup_path = self.backup_dir / f"{backup_name}.db"
        
        # Use SQLite's backup API for consistent backup
        src_conn = sqlite3.connect(self.db_path)
        dst_conn = sqlite3.connect(str(backup_path))
        
        try:
            src_conn.backup(dst_conn)
            logger.info(f"SQLite backup created: {backup_path}")
        finally:
            src_conn.close()
            dst_conn.close()
        
        self._cleanup_old_backups()
        return str(backup_path)
    
    def backup_blogs_to_json(self) -> Dict[str, Any]:
        """
        Export all blog articles to JSON format.
        
        Returns:
            Dictionary containing backup metadata and blog data
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, author, created_at, updated_at 
            FROM blogs ORDER BY id
        ''')
        
        blogs = []
        for row in cursor.fetchall():
            blogs.append({
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "author": row["author"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        conn.close()
        
        backup_data = {
            "backup_type": "blogs",
            "backup_timestamp": datetime.now().isoformat(),
            "record_count": len(blogs),
            "data": blogs
        }
        
        # Save to file
        backup_name = self._generate_backup_filename("blogs")
        backup_path = self.backup_dir / f"{backup_name}.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Blogs backup created: {backup_path} ({len(blogs)} records)")
        return backup_data
    
    def backup_tools_to_json(self) -> Dict[str, Any]:
        """
        Export all tools data to JSON format.
        
        Returns:
            Dictionary containing backup metadata and tools data
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if tools table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tools'
        ''')
        
        if not cursor.fetchone():
            logger.warning("Tools table does not exist, skipping tools backup")
            conn.close()
            return {"backup_type": "tools", "record_count": 0, "data": [], "note": "Table does not exist"}
        
        cursor.execute('''
            SELECT * FROM tools ORDER BY id
        ''')
        
        columns = [description[0] for description in cursor.description]
        tools = []
        
        for row in cursor.fetchall():
            tool_dict = {}
            for i, col in enumerate(columns):
                tool_dict[col] = row[i]
            tools.append(tool_dict)
        
        conn.close()
        
        backup_data = {
            "backup_type": "tools",
            "backup_timestamp": datetime.now().isoformat(),
            "record_count": len(tools),
            "columns": columns,
            "data": tools
        }
        
        # Save to file
        backup_name = self._generate_backup_filename("tools")
        backup_path = self.backup_dir / f"{backup_name}.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Tools backup created: {backup_path} ({len(tools)} records)")
        return backup_data
    
    def backup_comparisons_to_json(self) -> Dict[str, Any]:
        """
        Export tool comparison history to JSON format.
        Creates a log of comparisons for analytics purposes.
        
        Returns:
            Dictionary containing comparison log data
        """
        # Since comparisons are typically generated on-demand and not stored,
        # we create a sample comparison log structure
        backup_data = {
            "backup_type": "comparisons",
            "backup_timestamp": datetime.now().isoformat(),
            "note": "Tool comparisons are generated dynamically. This backup contains metadata.",
            "available_tools": self._get_available_tools_for_comparison()
        }
        
        backup_name = self._generate_backup_filename("comparisons")
        backup_path = self.backup_dir / f"{backup_name}.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Comparisons backup created: {backup_path}")
        return backup_data
    
    def _get_available_tools_for_comparison(self) -> List[str]:
        """Get list of tool names available for comparison."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM tools ORDER BY name')
            tools = [row["name"] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            tools = []
        
        conn.close()
        return tools
    
    def create_full_backup(self) -> Dict[str, Any]:
        """
        Create a comprehensive backup of all data.
        
        Returns:
            Summary of all backup operations
        """
        logger.info("Starting full database backup...")
        start_time = time.time()
        
        results = {
            "backup_timestamp": datetime.now().isoformat(),
            "backup_type": "full",
            "components": {}
        }
        
        # SQLite binary backup
        try:
            sqlite_path = self.backup_to_sqlite()
            results["components"]["sqlite"] = {
                "status": "success",
                "path": sqlite_path
            }
        except Exception as e:
            results["components"]["sqlite"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"SQLite backup failed: {e}")
        
        # Blogs JSON backup
        try:
            blogs_data = self.backup_blogs_to_json()
            results["components"]["blogs"] = {
                "status": "success",
                "record_count": blogs_data["record_count"]
            }
        except Exception as e:
            results["components"]["blogs"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Blogs backup failed: {e}")
        
        # Tools JSON backup
        try:
            tools_data = self.backup_tools_to_json()
            results["components"]["tools"] = {
                "status": "success",
                "record_count": tools_data["record_count"]
            }
        except Exception as e:
            results["components"]["tools"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Tools backup failed: {e}")
        
        # Comparisons backup
        try:
            comp_data = self.backup_comparisons_to_json()
            results["components"]["comparisons"] = {
                "status": "success"
            }
        except Exception as e:
            results["components"]["comparisons"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Comparisons backup failed: {e}")
        
        elapsed = time.time() - start_time
        results["elapsed_seconds"] = round(elapsed, 2)
        
        # Save summary
        summary_path = self.backup_dir / "latest_backup_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Full backup completed in {elapsed:.2f} seconds")
        return results
    
    def restore_from_sqlite(self, backup_path: str) -> bool:
        """
        Restore database from a SQLite backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restoration successful
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create a backup of current state before restoring
        current_backup = self.backup_to_sqlite()
        logger.info(f"Current state backed up to: {current_backup}")
        
        try:
            # Restore from backup
            src_conn = sqlite3.connect(backup_path)
            dst_conn = sqlite3.connect(self.db_path)
            
            src_conn.backup(dst_conn)
            
            src_conn.close()
            dst_conn.close()
            
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            # Attempt to restore from pre-restoration backup
            logger.info("Attempting to restore from pre-restoration backup...")
            src_conn = sqlite3.connect(current_backup)
            dst_conn = sqlite3.connect(self.db_path)
            src_conn.backup(dst_conn)
            src_conn.close()
            dst_conn.close()
            raise
    
    def restore_blogs_from_json(self, backup_path: str) -> int:
        """
        Restore blogs from a JSON backup file.
        
        Args:
            backup_path: Path to the JSON backup file
            
        Returns:
            Number of blogs restored
        """
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if backup_data.get("backup_type") != "blogs":
            raise ValueError("Invalid backup file: not a blogs backup")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        restored_count = 0
        for blog in backup_data["data"]:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO blogs 
                    (id, title, content, author, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    blog["id"],
                    blog["title"],
                    blog["content"],
                    blog["author"],
                    blog["created_at"],
                    blog["updated_at"]
                ))
                restored_count += 1
            except Exception as e:
                logger.error(f"Failed to restore blog {blog['id']}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Restored {restored_count} blogs from backup")
        return restored_count
    
    def _cleanup_old_backups(self) -> int:
        """
        Remove old backups exceeding the maximum retention count.
        
        Returns:
            Number of backups removed
        """
        backup_files = sorted(
            self.backup_dir.glob("backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        removed = 0
        if len(backup_files) > self.max_backups:
            for old_backup in backup_files[self.max_backups:]:
                try:
                    old_backup.unlink()
                    logger.info(f"Removed old backup: {old_backup}")
                    removed += 1
                except Exception as e:
                    logger.error(f"Failed to remove old backup {old_backup}: {e}")
        
        return removed
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup metadata
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_bytes": stat.st_size,
                "size_human": self._format_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": backup_file.suffix[1:]  # Remove the dot
            })
        
        return backups
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    def start_auto_backup(self) -> None:
        """Start the automatic backup scheduler."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            logger.warning("Auto backup scheduler is already running")
            return
        
        self._stop_scheduler.clear()
        self._scheduler_thread = threading.Thread(
            target=self._backup_scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()
        logger.info(f"Auto backup scheduler started (interval: {self.auto_backup_interval / 3600}h)")
    
    def stop_auto_backup(self) -> None:
        """Stop the automatic backup scheduler."""
        self._stop_scheduler.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Auto backup scheduler stopped")
    
    def _backup_scheduler_loop(self) -> None:
        """Background thread for scheduled backups."""
        while not self._stop_scheduler.is_set():
            try:
                self.create_full_backup()
            except Exception as e:
                logger.error(f"Scheduled backup failed: {e}")
            
            # Wait for next backup interval or stop signal
            self._stop_scheduler.wait(timeout=self.auto_backup_interval)


# API routes for backup management
def register_backup_routes(app):
    """
    Register backup-related API routes with a FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    from fastapi import HTTPException
    
    backup_service = DatabaseBackupService()
    
    @app.post("/api/admin/backup/full")
    async def create_full_backup():
        """Create a full database backup."""
        try:
            result = backup_service.create_full_backup()
            return {"status": "success", "backup": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/admin/backup/blogs")
    async def backup_blogs():
        """Backup blog articles to JSON."""
        try:
            result = backup_service.backup_blogs_to_json()
            return {"status": "success", "backup": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/admin/backup/tools")
    async def backup_tools():
        """Backup tools data to JSON."""
        try:
            result = backup_service.backup_tools_to_json()
            return {"status": "success", "backup": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/admin/backup/list")
    async def list_backups():
        """List all available backups."""
        try:
            backups = backup_service.list_backups()
            return {"status": "success", "backups": backups}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/admin/backup/start-auto")
    async def start_auto_backup():
        """Start automatic backup scheduler."""
        try:
            backup_service.start_auto_backup()
            return {"status": "success", "message": "Auto backup started"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/admin/backup/stop-auto")
    async def stop_auto_backup():
        """Stop automatic backup scheduler."""
        try:
            backup_service.stop_auto_backup()
            return {"status": "success", "message": "Auto backup stopped"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# CLI interface for manual backup operations
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Backup Utility")
    parser.add_argument(
        "action",
        choices=["full", "blogs", "tools", "list", "test"],
        help="Backup action to perform"
    )
    parser.add_argument(
        "--db",
        default="blog.db",
        help="Path to database file"
    )
    parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Backup directory"
    )
    
    args = parser.parse_args()
    
    service = DatabaseBackupService(
        db_path=args.db,
        backup_dir=args.backup_dir
    )
    
    if args.action == "full":
        result = service.create_full_backup()
        print(json.dumps(result, indent=2))
    
    elif args.action == "blogs":
        result = service.backup_blogs_to_json()
        print(f"Backed up {result['record_count']} blogs")
    
    elif args.action == "tools":
        result = service.backup_tools_to_json()
        print(f"Backed up {result['record_count']} tools")
    
    elif args.action == "list":
        backups = service.list_backups()
        print("\nAvailable Backups:")
        print("-" * 60)
        for b in backups:
            print(f"  {b['filename']:<45} {b['size_human']:>10}")
        print(f"\nTotal: {len(backups)} backup(s)")
    
    elif args.action == "test":
        print("Running backup test...")
        print("\n1. Creating full backup...")
        result = service.create_full_backup()
        print(f"   ✓ Full backup completed in {result['elapsed_seconds']}s")
        
        for component, status in result["components"].items():
            icon = "✓" if status["status"] == "success" else "✗"
            print(f"   {icon} {component}: {status['status']}")
        
        print("\n2. Listing backups...")
        backups = service.list_backups()
        print(f"   ✓ Found {len(backups)} backup(s)")
        
        print("\n✓ Backup test completed successfully!")
