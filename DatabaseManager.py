import psycopg2
from psycopg2 import sql, DatabaseError
from contextlib import contextmanager
from Utils.utils import parse_column_detail
from Utils.dbInfo import *

class DatabaseManager:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """Initialize the database manager with connection parameters."""
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.init_query = init_query
        
        self.execute_query(self.init_query)
        
        self.data_column_names = [name.lower() for name in parse_column_detail(data_table_details)]
        self.config_column_names = [name.lower() for name in parse_column_detail(config_table_details)]
        self.create_table(config_table_name, self.config_column_names, config_table_details)
        self.create_table(data_table_name, self.data_column_names, data_table_details)

    def _connect(self):
        """Private method to establish a database connection."""
        try:
            connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            return connection
        except DatabaseError as e:
            print(f"Error while connecting to database: {e}")
            raise

    @contextmanager
    def get_cursor(self):
        """Context manager for handling database cursor."""
        connection = None
        cursor = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            yield cursor  # Provide cursor to the caller
            connection.commit()  # Commit changes after operations
        except Exception as e:
            if connection:
                connection.rollback()  # Rollback on error
            print(f"Error executing database operation: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def execute_query(self, query, params=None):
        """Execute a simple query like INSERT, UPDATE, or DELETE."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

    def fetch_all(self, query, params=None):
        """Execute a SELECT query and return all rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=None):
        """Execute a SELECT query and return a single row."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def store_frame(self, data, frame_type):
        if frame_type == 0:
            tableName = data_table_name
            tableDetails = data_table_details
        elif frame_type & 2 != 0 or frame_type == 5:
            tableName = config_table_name
            tableDetails = config_table_details
        else:
            raise NotImplementedError(f"No method to store the frame {frame_type}.")
        
        names, placeholders = parse_column_detail(tableDetails)
        
        assert len(names) == len(data[0]), f"Number of columns({len(names)}) does not matches with data({len(data[0])})"
        
        names = ', '.join(names)
        placeholders = ', '.join(placeholders)

        for row in data:
            query = f"INSERT INTO {tableName} ({names}) VALUES ({placeholders});"
            self.execute_query(query, row)

    
    def create_table(self, table_name, column_names, column_details):
        """
        Creates a new table in PostgreSQL if it doesn't already exist or if the column details are different.

        Args:
        - table_name: Name of the table to create (string).
        - column_names: List of column names (list of strings).
        - column_details: Column definitions (string, e.g., "id SERIAL PRIMARY KEY, name VARCHAR(100)").
        """
        try:
            # Check if the table exists
            check_table_query = f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s;
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(check_table_query, (table_name,))
                table_exists = cursor.fetchone() is not None
            
            if table_exists:
                print(f"Table '{table_name}' already exists. Checking columns...")

                # Check if columns match
                check_columns_query = f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s;
                """
                with self.get_cursor() as cursor:
                    cursor.execute(check_columns_query, (table_name,))
                    existing_column_names = [names[0] for names in cursor.fetchall()]

                print("Existing columns:", existing_column_names)
                print("New columns:", column_names)

                # Compare existing columns with new ones
                if existing_column_names == column_names:
                    print(f"Table '{table_name}' already has the same columns.")
                    return
                else:
                    print(f"Table '{table_name}' exists, but columns do not match. Dropping and recreating...")
                    # Drop the table if columns don't match
                    self.execute_query(f"DROP TABLE IF EXISTS {table_name};")
            
            # Create the table if it does not exist or after dropping it
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_details});"
            self.execute_query(create_table_query)
            print(f"Table '{table_name}' created successfully.")

        except Exception as e:
            print(f"Error creating table '{table_name}': {e}")

