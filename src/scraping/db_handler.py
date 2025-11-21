"""
Database handler for storing car listings in PostgreSQL.
"""
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, Optional
import yaml
from pathlib import Path


class CarDatabase:
    """Handler for PostgreSQL database operations."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize database connection.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.conn = None
        self.cursor = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load database configuration from YAML file."""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('database', {})
        else:
            # Default configuration
            return {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'car_data',
                'user': 'postgres',
                'password': 'your_password',
                'table_name': 'car_listings'
            }
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        dbname = self.config.get('dbname', 'car_data')
        
        try:
            # First try to connect to the target database
            self.conn = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                dbname=dbname,
                user=self.config.get('user', 'postgres'),
                password=self.config.get('password', '')
            )
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to PostgreSQL database: {dbname}")
            return True
        except psycopg2.OperationalError as e:
            if "does not exist" in str(e):
                # Database doesn't exist, create it
                print(f"⚠ Database '{dbname}' does not exist. Creating it now...")
                try:
                    # Connect to default 'postgres' database to create new database
                    conn_temp = psycopg2.connect(
                        host=self.config.get('host', 'localhost'),
                        port=self.config.get('port', 5432),
                        dbname='postgres',
                        user=self.config.get('user', 'postgres'),
                        password=self.config.get('password', '')
                    )
                    conn_temp.autocommit = True
                    cursor_temp = conn_temp.cursor()
                    cursor_temp.execute(f"CREATE DATABASE {dbname};")
                    cursor_temp.close()
                    conn_temp.close()
                    print(f"✓ Database '{dbname}' created successfully!")
                    print("="*60)
                    
                    # Now connect to the newly created database
                    self.conn = psycopg2.connect(
                        host=self.config.get('host', 'localhost'),
                        port=self.config.get('port', 5432),
                        dbname=dbname,
                        user=self.config.get('user', 'postgres'),
                        password=self.config.get('password', '')
                    )
                    self.cursor = self.conn.cursor()
                    print(f"✓ Connected to PostgreSQL database: {dbname}")
                    return True
                except Exception as create_error:
                    print(f"✗ Error creating database: {create_error}")
                    return False
            else:
                print(f"✗ Error connecting to database: {e}")
                return False
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def create_table(self):
        """Create car_listings table if it doesn't exist."""
        table_name = self.config.get('table_name', 'car_listings')
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            url VARCHAR(500) PRIMARY KEY,
            price BIGINT,
            brand VARCHAR(100),
            model VARCHAR(200),
            year INTEGER,
            odometer INTEGER,
            transmission VARCHAR(50),
            fuel_type VARCHAR(50),
            engine_capacity VARCHAR(20),
            body_style VARCHAR(50),
            origin VARCHAR(100),
            seats VARCHAR(20),
            condition VARCHAR(50),
            num_owners VARCHAR(50),
            inspection_status VARCHAR(50),
            warranty_status VARCHAR(50),
            source VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print(f"✓ Table '{table_name}' is ready")
            return True
        except Exception as e:
            print(f"✗ Error creating table: {e}")
            self.conn.rollback()
            return False
    
    def insert_car(self, car_data: Dict[str, str]) -> bool:
        """
        Insert a car record into the database.
        If URL already exists, ignore and return False.
        
        Args:
            car_data: Dictionary containing car information
            
        Returns:
            True if inserted, False if URL exists or error occurred
        """
        table_name = self.config.get('table_name', 'car_listings')
        
        # Convert -1 to NULL for proper database storage
        processed_data = {}
        for key, value in car_data.items():
            if value == -1 or value == '-1':
                processed_data[key] = None
            else:
                processed_data[key] = value
        
        insert_query = f"""
        INSERT INTO {table_name} (
            url, price, brand, model, year, odometer, transmission,
            fuel_type, engine_capacity, body_style, origin, seats,
            condition, num_owners, inspection_status, warranty_status, source
        ) VALUES (
            %(url)s, %(price)s, %(brand)s, %(model)s, %(year)s, %(odometer)s,
            %(transmission)s, %(fuel_type)s, %(engine_capacity)s, %(body_style)s,
            %(origin)s, %(seats)s, %(condition)s, %(num_owners)s,
            %(inspection_status)s, %(warranty_status)s, %(source)s
        )
        ON CONFLICT (url) DO NOTHING;
        """
        
        try:
            self.cursor.execute(insert_query, processed_data)
            self.conn.commit()
            
            # Check if row was inserted
            if self.cursor.rowcount > 0:
                return True
            else:
                # URL already exists
                return False
        except Exception as e:
            print(f"  ✗ Error inserting car: {e}")
            self.conn.rollback()
            return False
    
    def url_exists(self, url: str) -> bool:
        """
        Check if a URL already exists in the database.
        
        Args:
            url: Car listing URL
            
        Returns:
            True if URL exists, False otherwise
        """
        table_name = self.config.get('table_name', 'car_listings')
        query = f"SELECT 1 FROM {table_name} WHERE url = %s LIMIT 1;"
        
        try:
            self.cursor.execute(query, (url,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"  ✗ Error checking URL: {e}")
            return False
    
    def get_total_count(self) -> int:
        """Get total number of records in database."""
        table_name = self.config.get('table_name', 'car_listings')
        query = f"SELECT COUNT(*) FROM {table_name};"
        
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"  ✗ Error getting count: {e}")
            return 0
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        connected = self.connect()
        if not connected:
            raise ConnectionError("Failed to connect to PostgreSQL database. Please check your config.yaml settings.")
        
        table_created = self.create_table()
        if not table_created:
            raise RuntimeError("Failed to create database table. Check database permissions.")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
