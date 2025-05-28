import os
import sqlite3

import pandas as pd  # Import pandas for CSV handling

import ingenious.common.config.config as Config


class sqlite_sample_db:
    def __init__(self):
        self._config = Config.get_config()

        self.db_path = self._config.local_sql_db.database_path
        db_dir_check = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir_check):
            os.makedirs(db_dir_check)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_table()
        self._load_csv_data()

    def execute_sql(self, sql, params=[], expect_results=True):
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row  # Set row factory to sqlite3.Row
            cursor = connection.cursor()

            if expect_results:
                res = cursor.execute(sql, params)
                rows = res.fetchall()
                result = [dict(row) for row in rows]
                return result
            else:
                connection.execute(sql, params)
                connection.commit()

        except sqlite3.Error as e:
            # Display the exception
            print(e)

        finally:
            if connection:
                connection.close()

    def _create_table(self):
        with self.connection:
            # Create table for the CSV data
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS students_performance (
                    gender TEXT,
                    race_ethnicity TEXT,
                    parental_education TEXT,
                    lunch TEXT,
                    test_prep_course TEXT,
                    math_score INTEGER,
                    reading_score INTEGER,
                    writing_score INTEGER
                );
            """)

    def _load_csv_data(self):
        # Load CSV file into a DataFrame
        csv_path = self._config.local_sql_db.sample_csv_path
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Load data into the students_performance table
            with self.connection:
                df.to_sql(
                    "sample_data", self.connection, if_exists="replace", index=False
                )
            print("CSV data loaded into sample_data table.")
        else:
            print(f"CSV file not found at {csv_path}.")
