"""
QueryVerse Backend - Fixed version with working upload and DBT
Run with: python backend.py
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import duckdb
import os
import aiofiles
import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlparse
from datetime import datetime
import shutil
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="QueryVerse API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATABASE_PATH = "./queryverse.db"
UPLOAD_DIR = "./uploads"
DBT_DIR = "./dbt_models"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DBT_DIR, exist_ok=True)

class DataManager:
    """Handles all data operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database with basic schema"""
        try:
            conn = duckdb.connect(self.db_path)
            conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
            conn.execute("CREATE SCHEMA IF NOT EXISTS staging") 
            conn.execute("CREATE SCHEMA IF NOT EXISTS marts")
            logger.info("Database initialized successfully")
            conn.close()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def create_raw_table(self, filename: str, df: pd.DataFrame):
        """Create raw table from uploaded data"""
        try:
            conn = duckdb.connect(self.db_path)
            
            # Clean filename for table name
            table_name = filename.lower().replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
            table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)
            table_name = f"raw_{table_name}"
            
            # Clean column names
            df.columns = [str(col).lower().replace(' ', '_').replace('-', '_').replace('.', '_') 
                         for col in df.columns]
            
            # Remove any completely empty columns
            df = df.dropna(axis=1, how='all')
            
            # Replace NaN with None for better handling
            df = df.where(pd.notnull(df), None)
            
            # Drop and recreate table
            conn.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
            
            # Create table from dataframe
            conn.register('temp_df', df)
            conn.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM temp_df")
            
            # Verify table was created
            result = conn.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()
            logger.info(f"Created table raw.{table_name} with {result[0]} rows")
            
            conn.close()
            return table_name
            
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise e
    
    def get_tables(self):
        """Get all tables"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("""
                SELECT table_schema, table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns 
                        WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')
                ORDER BY table_schema, table_name
            """).fetchall()
            conn.close()
            
            tables = []
            for row in result:
                tables.append({
                    "schema": row[0],
                    "name": row[1],
                    "full_name": f"{row[0]}.{row[1]}",
                    "columns": row[2]
                })
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    def execute_query(self, query: str):
        """Execute SQL query"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description] if conn.description else []
            conn.close()
            
            return {
                "success": True,
                "data": [dict(zip(columns, row)) for row in result],
                "columns": columns,
                "row_count": len(result)
            }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}

class SimpleDBTManager:
    """Simplified DBT manager that works without complex setup"""
    
    def __init__(self):
        self.dbt_dir = Path(DBT_DIR)
        self.init_simple_dbt()
    
    def init_simple_dbt(self):
        """Initialize a simple DBT-like structure"""
        try:
            self.dbt_dir.mkdir(exist_ok=True)
            
            # Create models directory
            models_dir = self.dbt_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            # Create a simple staging directory
            staging_dir = models_dir / "staging"
            staging_dir.mkdir(exist_ok=True)
            
            logger.info("Simple DBT structure initialized")
            
        except Exception as e:
            logger.error(f"DBT initialization failed: {e}")
    
    def create_staging_model(self, table_name: str):
        """Create a simple staging model"""
        try:
            model_sql = f"""
-- Staging model for {table_name}
-- This is a simple transformation example
SELECT 
    *,
    CURRENT_TIMESTAMP as _loaded_at,
    '{table_name}' as _source_table
FROM raw.{table_name}
"""
            
            model_file = self.dbt_dir / "models" / "staging" / f"stg_{table_name}.sql"
            with open(model_file, "w") as f:
                f.write(model_sql)
            
            logger.info(f"Created staging model: {model_file}")
            return str(model_file)
            
        except Exception as e:
            logger.error(f"Failed to create staging model: {e}")
            return None
    
    def run_transformation(self, table_name: str):
        """Run a simple transformation without full DBT"""
        try:
            conn = duckdb.connect(DATABASE_PATH)
            
            # Create staging schema if not exists
            conn.execute("CREATE SCHEMA IF NOT EXISTS staging")
            
            # Create a simple staging table
            staging_query = f"""
            CREATE OR REPLACE TABLE staging.stg_{table_name} AS
            SELECT 
                *,
                CURRENT_TIMESTAMP as _loaded_at,
                '{table_name}' as _source_table
            FROM raw.{table_name}
            """
            
            conn.execute(staging_query)
            
            # Get row count
            result = conn.execute(f"SELECT COUNT(*) FROM staging.stg_{table_name}").fetchone()
            row_count = result[0]
            
            conn.close()
            
            return {
                "success": True,
                "message": f"Created staging.stg_{table_name} with {row_count} rows",
                "table_created": f"staging.stg_{table_name}"
            }
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_simple_dbt(self, command: str):
        """Run simple DBT-like operations"""
        try:
            if command == "run":
                # Get all raw tables and create staging versions
                conn = duckdb.connect(DATABASE_PATH)
                tables = conn.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'raw'
                """).fetchall()
                conn.close()
                
                if not tables:
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": "No raw tables found to transform"
                    }
                
                results = []
                for table in tables:
                    table_name = table[0]
                    result = self.run_transformation(table_name)
                    if result["success"]:
                        results.append(f"✅ Transformed {table_name}")
                    else:
                        results.append(f"❌ Failed to transform {table_name}: {result['error']}")
                
                return {
                    "success": True,
                    "stdout": "\n".join(results),
                    "stderr": ""
                }
                
            elif command == "test":
                # Simple data quality tests
                conn = duckdb.connect(DATABASE_PATH)
                tests = []
                
                # Test 1: Check for empty tables
                staging_tables = conn.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'staging'
                """).fetchall()
                
                for table in staging_tables:
                    table_name = table[0]
                    count = conn.execute(f"SELECT COUNT(*) FROM staging.{table_name}").fetchone()[0]
                    if count > 0:
                        tests.append(f"✅ staging.{table_name} has {count} rows")
                    else:
                        tests.append(f"❌ staging.{table_name} is empty")
                
                conn.close()
                
                return {
                    "success": True,
                    "stdout": "\n".join(tests) if tests else "No staging tables to test",
                    "stderr": ""
                }
                
            elif command == "docs generate":
                # Generate simple documentation
                conn = duckdb.connect(DATABASE_PATH)
                
                # Get table information
                tables_info = conn.execute("""
                    SELECT table_schema, table_name, 
                           (SELECT COUNT(*) FROM information_schema.columns 
                            WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema IN ('raw', 'staging')
                    ORDER BY table_schema, table_name
                """).fetchall()
                
                conn.close()
                
                docs = ["📚 QueryVerse Data Documentation", "=" * 40]
                current_schema = None
                
                for schema, table, col_count in tables_info:
                    if schema != current_schema:
                        docs.append(f"\n📁 {schema.upper()} SCHEMA:")
                        current_schema = schema
                    docs.append(f"  📋 {table} ({col_count} columns)")
                
                return {
                    "success": True,
                    "stdout": "\n".join(docs),
                    "stderr": ""
                }
                
            else:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Unknown command: {command}"
                }
                
        except Exception as e:
            logger.error(f"DBT operation failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }

# Initialize managers
data_manager = DataManager()
dbt_manager = SimpleDBTManager()

# Routes
@app.get("/")
async def root():
    return {"message": "QueryVerse API is running!", "timestamp": datetime.now().isoformat()}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process dataset - FIXED VERSION"""
    logger.info(f"Received upload request for: {file.filename}")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file format. Use: {allowed_extensions}")
        
        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Read file content
        content = await file.read()
        
        # Write to disk
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File saved to: {file_path}")
        
        # Read file into DataFrame with robust CSV handling
        try:
            if file_ext == '.csv':
                # Try multiple strategies for reading CSV files
                df = None
                strategies = [
                    # Strategy 1: Standard reading
                    {'encoding': 'utf-8'},
                    {'encoding': 'latin-1'},
                    {'encoding': 'cp1252'},
                    # Strategy 2: Handle malformed CSV with error handling
                    {'encoding': 'utf-8', 'error_bad_lines': False, 'warn_bad_lines': True},
                    {'encoding': 'latin-1', 'error_bad_lines': False, 'warn_bad_lines': True},
                    # Strategy 3: More robust parsing
                    {'encoding': 'utf-8', 'sep': ',', 'quotechar': '"', 'on_bad_lines': 'skip'},
                    {'encoding': 'latin-1', 'sep': ',', 'quotechar': '"', 'on_bad_lines': 'skip'},
                    # Strategy 4: Very permissive parsing
                    {'encoding': 'utf-8', 'sep': ',', 'quotechar': '"', 'on_bad_lines': 'skip', 'skipinitialspace': True},
                    # Strategy 5: Last resort - read with no header inference
                    {'encoding': 'utf-8', 'header': None, 'on_bad_lines': 'skip'},
                ]
                
                for i, strategy in enumerate(strategies):
                    try:
                        logger.info(f"Trying CSV parsing strategy {i+1}: {strategy}")
                        df = pd.read_csv(file_path, **strategy)
                        logger.info(f"Strategy {i+1} successful! DataFrame shape: {df.shape}")
                        break
                    except Exception as e:
                        logger.warning(f"Strategy {i+1} failed: {e}")
                        continue
                
                # If all strategies failed, try reading line by line and fixing issues
                if df is None:
                    logger.info("All standard strategies failed. Trying manual line-by-line parsing...")
                    try:
                        # Read file line by line and clean it
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Get the header
                        header = lines[0].strip().split(',')
                        expected_cols = len(header)
                        logger.info(f"Expected columns: {expected_cols}, Header: {header}")
                        
                        # Clean the data lines
                        cleaned_lines = [lines[0]]  # Keep header
                        for i, line in enumerate(lines[1:], 2):
                            parts = line.strip().split(',')
                            if len(parts) == expected_cols:
                                cleaned_lines.append(line)
                            elif len(parts) > expected_cols:
                                # Try to merge extra fields
                                fixed_parts = parts[:expected_cols-1] + [','.join(parts[expected_cols-1:])]
                                cleaned_lines.append(','.join(fixed_parts) + '\n')
                                logger.warning(f"Fixed line {i}: had {len(parts)} fields, expected {expected_cols}")
                            else:
                                # Skip lines with too few fields
                                logger.warning(f"Skipped line {i}: had {len(parts)} fields, expected {expected_cols}")
                        
                        # Save cleaned CSV to temporary file
                        temp_file = file_path + '.cleaned'
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.writelines(cleaned_lines)
                        
                        # Try to read the cleaned file
                        df = pd.read_csv(temp_file, encoding='utf-8')
                        logger.info(f"Manual cleaning successful! DataFrame shape: {df.shape}")
                        
                        # Clean up temp file
                        os.remove(temp_file)
                        
                    except Exception as e:
                        logger.error(f"Manual parsing also failed: {e}")
                        raise HTTPException(status_code=400, detail=f"Unable to parse CSV file. The file appears to be malformed. Error: {str(e)}")
                
                if df is None:
                    raise HTTPException(status_code=400, detail="Unable to read CSV file with any parsing strategy")
                    
            elif file_ext in ['.xlsx', '.xls']:
                try:
                    df = pd.read_excel(file_path)
                except Exception as e:
                    logger.error(f"Failed to read Excel file: {e}")
                    raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            logger.info(f"Final DataFrame created with shape: {df.shape}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        # Validate DataFrame
        if df.empty:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Create raw table
        try:
            table_name = data_manager.create_raw_table(file.filename, df)
            logger.info(f"Created table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")
        
        # Create staging model
        staging_model = dbt_manager.create_staging_model(table_name)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        result = {
            "success": True,
            "filename": file.filename,
            "table_name": f"raw.{table_name}",
            "rows": len(df),
            "columns": list(df.columns),
            "staging_model": staging_model,
            "message": f"Successfully uploaded {file.filename} with {len(df)} rows and {len(df.columns)} columns"
        }
        
        logger.info(f"Upload successful: {result}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/tables")
async def get_tables():
    """Get all tables"""
    try:
        tables = data_manager.get_tables()
        return {"success": True, "tables": tables}
    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        return {"success": False, "error": str(e)}

@app.post("/query")
async def execute_query(query_data: dict):
    """Execute SQL query"""
    try:
        query = query_data.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"Executing query: {query[:100]}...")
        result = data_manager.execute_query(query)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/dbt/{command}")
async def run_dbt_command(command: str):
    """Run simplified DBT command"""
    try:
        valid_commands = ["run", "test", "docs generate"]
        if command not in valid_commands:
            raise HTTPException(status_code=400, detail=f"Invalid command. Use: {valid_commands}")
        
        logger.info(f"Running DBT command: {command}")
        result = dbt_manager.run_simple_dbt(command)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DBT command error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/analytics")
async def get_analytics():
    """Get platform analytics"""
    try:
        tables = data_manager.get_tables()
        
        # Get row counts for each table
        total_rows = 0
        conn = duckdb.connect(DATABASE_PATH)
        
        for table in tables:
            try:
                result = conn.execute(f"SELECT COUNT(*) FROM {table['full_name']}").fetchone()
                if result:
                    total_rows += result[0]
            except Exception as e:
                logger.warning(f"Failed to count rows for {table['full_name']}: {e}")
                continue
        
        conn.close()
        
        return {
            "success": True,
            "summary": {
                "total_tables": len(tables),
                "total_rows": total_rows,
                "last_updated": datetime.now().isoformat(),
                "schemas": list(set(table["schema"] for table in tables))
            }
        }
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = duckdb.connect(DATABASE_PATH)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Serve the frontend HTML file
@app.get("/app")
async def serve_frontend():
    """Serve the frontend HTML"""
    try:
        return FileResponse("frontend.html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")

if __name__ == "__main__":
    print("🚀 Starting QueryVerse Backend...")
    print("📊 Access the app at: http://localhost:8000/app")
    print("📋 API docs at: http://localhost:8000/docs")
    print("🏥 Health check at: http://localhost:8000/health")
    print("🔄 Auto-reload enabled for development")
    
    # Test database on startup
    try:
        conn = duckdb.connect(DATABASE_PATH)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)