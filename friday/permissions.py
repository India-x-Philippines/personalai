"""
F.R.I.D.A.Y. Permission Manager
Evaluates granular security permissions for application control and file operations.
"""

import json
import os
import logging

logger = logging.getLogger("friday-permissions")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "permissions.json")

class PermissionManager:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.permissions = self._load_permissions()

    def _load_permissions(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load permissions file: {e}")
        return self._default_permissions()

    def _default_permissions(self) -> dict:
        return {
            "apps": {
                "microsoft_photos": {
                    "enabled": True,
                    "permissions": {
                        "read_images": "ALLOW",
                        "edit_images": "ALLOW",
                        "create_images": "ALLOW",
                        "modify_original": "ASK",
                        "delete_images": "DENY"
                    }
                }
            }
        }

    def check_permission(self, app_name: str, capability: str) -> str:
        """
        Returns 'ALLOW', 'ASK', or 'DENY'.
        """
        app_config = self.permissions.get("apps", {}).get(app_name)
        if not app_config or not app_config.get("enabled", False):
            return "DENY"

        capability_status = app_config.get("permissions", {}).get(capability, "DENY")
        logger.info(f"Permission check for {app_name}.{capability} -> {capability_status}")
        return capability_status

# Global singleton instance
permission_manager = PermissionManager()
