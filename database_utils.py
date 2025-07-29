from sqlalchemy import create_engine, text
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from config import settings  # Import settings to get the connection string
from utils import logger  # Import logger


class DatabaseManager:
    """
    Manages connections and operations for the SQL Server database.
    Uses SQLAlchemy for connectivity.
    """

    def __init__(self):
        try:
            connection_string = (
                "mssql+pyodbc://@alinatics/StudentMarks"
                "?driver=ODBC+Driver+17+for+SQL+Server"
                "&trusted_connection=yes"
            )
            self.engine = create_engine(connection_string)
            logger.info("Successfully initialized SQLAlchemy engine.")
        except Exception as e:
            logger.error(f"Failed to initialize SQLAlchemy engine: {e}", exc_info=True)
            self.engine = None

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Executes a SQL query and returns results as a list of dictionaries."""
        if not self.engine:
            logger.error("Cannot execute query: No active SQLAlchemy engine.")
            return []

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = [dict(row._mapping) for row in result]  # ✅ FIXED HERE
                logger.debug(f"Query executed successfully: {query[:100]}...")
                return rows
        except Exception as e:
            logger.error(
                f"Error executing query '{query[:100]}...': {e}", exc_info=True
            )
            return []

    def execute_non_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Executes a SQL query that does not return results (e.g., INSERT, UPDATE, DELETE)."""
        if not self.engine:
            logger.error("Cannot execute non-query: No active SQLAlchemy engine.")
            return 0

        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                rows_affected = result.rowcount
                logger.debug(
                    f"Non-query executed successfully: {query[:100]}... Rows affected: {rows_affected}"
                )
                return rows_affected
        except Exception as e:
            logger.error(
                f"Error executing non-query '{query[:100]}...': {e}", exc_info=True
            )
            return 0

    def fetch_data_as_dataframe(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Fetches data from the database and returns it as a pandas DataFrame."""
        if not self.engine:
            logger.error("Cannot fetch data as DataFrame: No active SQLAlchemy engine.")
            return pd.DataFrame()

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn, params=params or {})
                logger.debug(
                    f"Data fetched into DataFrame successfully: {query[:100]}..."
                )
                return df
        except Exception as e:
            logger.error(
                f"Error fetching data into DataFrame '{query[:100]}...': {e}",
                exc_info=True,
            )
            return pd.DataFrame()

    def get_lookup_data(self, table_name: str) -> pd.DataFrame:
        """Fetches data from a specific lookup table."""
        query = f"SELECT * FROM {table_name}"
        logger.info(f"Fetching lookup data for table: {table_name}")
        return self.fetch_data_as_dataframe(query)


# Initialize the database manager globally for easy access
db_manager = DatabaseManager()

# Example Usage:
if __name__ == "__main__":
    try:
        gender_df = db_manager.get_lookup_data("gender_lookup")
        if not gender_df.empty:
            print("\nGender Lookup Data:")
            print(gender_df.head())
        else:
            print(
                "\nCould not fetch gender_lookup data. Ensure table exists and connection is valid."
            )

        # Uncomment to test non-query and query examples
        # rows_affected = db_manager.execute_non_query(
        #     "INSERT INTO test_table (id, name) VALUES (:id, :name)", {"id": 1, "name": "Test Name"}
        # )
        # print(f"\nRows affected by insert: {rows_affected}")

        # data = db_manager.execute_query("SELECT TOP 5 * FROM Students")
        # if data:
        #     print("\nSample Student Data (list of dicts):")
        #     for row in data:
        #         print(row)
        # else:
        #     print("\nCould not fetch sample student data.")

    except Exception as e:
        logger.error(
            f"An error occurred during database_utils test: {e}", exc_info=True
        )
