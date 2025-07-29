# config.py

import configparser
import os
from typing import Dict, Any
from utils import logger  # Import logger from utils.py


class Settings:
    """
    Manages application settings, including database connection details
    loaded from config.ini.
    """

    def __init__(self, config_file: str = "config.ini"):
        self.config = configparser.ConfigParser()

        # Always attempt to read the config file first
        read_success = self.config.read(config_file)

        # Check if the file was read successfully AND if the required section exists
        # If not, create/overwrite the dummy config and re-read
        if not read_success or "DatabaseConnection" not in self.config:
            logger.warning(
                f"Configuration file '{config_file}' not found or missing 'DatabaseConnection' section. Creating/updating dummy config."
            )
            self._create_dummy_config(config_file)
            # After creating/updating, re-read the config to ensure it's loaded
            self.config.read(config_file)
            logger.info(
                f"Dummy '{config_file}' created/updated. Please update with your actual credentials if they are not already set."
            )

        self._load_database_settings()
        self._load_app_settings()

    def _create_dummy_config(self, config_file: str):
        """
        Creates a dummy config.ini file if it doesn't exist,
        using the correct ODBC driver format.
        """
        self.config["DatabaseConnection"] = (
            {  # Changed section name to match user's config.ini
                "DRIVER": "{ODBC Driver 17 for SQL Server}",  # Use curly braces for driver name
                "SERVER": "your_server_name",  # Placeholder
                "DATABASE": "your_database_name",  # Placeholder
                "Trusted_Connection": "yes",  # Or "no" if using User ID/Password
                # Add User ID and Password if Trusted_Connection is 'no'
                # "UID": "your_username",
                # "PWD": "your_password",
            }
        )
        with open(config_file, "w") as f:
            self.config.write(f)

    def _load_database_settings(self):
        """
        Loads ODBC connection string components from the 'DatabaseConnection' section.
        """
        # Ensure the section name matches what's in config.ini
        if "DatabaseConnection" not in self.config:
            logger.error("Missing 'DatabaseConnection' section in config.ini")
            raise ValueError("Missing 'DatabaseConnection' section in config.ini")

        db_params = self.config["DatabaseConnection"]

        # Construct the connection string directly from the keys in config.ini
        # Ensure DRIVER value is wrapped in curly braces if it's not already
        driver = db_params.get("DRIVER", "").strip()
        if not driver.startswith("{") and not driver.endswith("}"):
            driver = f"{{{driver}}}"

        connection_parts = [
            f"DRIVER={driver}",
            f"SERVER={db_params.get('SERVER', '')}",
            f"DATABASE={db_params.get('DATABASE', '')}",
        ]

        # Add authentication details based on Trusted_Connection
        if db_params.get("Trusted_Connection", "no").lower() == "yes":
            connection_parts.append("Trusted_Connection=yes")
        else:
            if db_params.get("UID") and db_params.get("PWD"):
                connection_parts.append(f"UID={db_params['UID']}")
                connection_parts.append(f"PWD={db_params['PWD']}")
            else:
                logger.warning(
                    "Trusted_Connection is not 'yes' but UID/PWD are missing. Connection might fail."
                )

        # Filter out empty parts and join
        self.db_connection_string = ";".join(
            [part for part in connection_parts if "=" in part]
        )
        logger.info("Database connection string loaded.")

    def _load_app_settings(self):
        """
        Loads general application settings.
        """
        self.APP_TITLE_MAIN = "RISE - Results Intelligence & Student Evaluation"
        self.APP_TITLE_SUB = "Uplifting and growth-oriented"
        self.APP_TITLE = f"{self.APP_TITLE_MAIN}: {self.APP_TITLE_SUB}"
        logger.info("Application settings loaded.")


# Initialize settings globally for easy access
settings = Settings()

# Example Usage:
if __name__ == "__main__":
    print("Database Connection String:")
    print(settings.db_connection_string)
    print("\nApplication Title:")
    print(settings.APP_TITLE)
    print(f"Main Title: {settings.APP_TITLE_MAIN}")
    print(f"Sub Title: {settings.APP_TITLE_SUB}")
