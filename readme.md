# QueryVerse - Complete Data Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-yellow.svg)](https://duckdb.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

A complete data platform with SQL query engine, DBT transformations, and interactive analytics dashboard. Upload CSV/Excel files, transform data, execute custom SQL queries, and visualize results - all in one seamless interface.

![QueryVerse Dashboard](screenshots/upload.png)

## Features

-  **Easy Data Upload** - Drag & drop CSV/Excel files with automatic schema detection and robust parsing
- **Dataset Creator** - Build datasets manually with spreadsheet-like interface  
- **SQL Query Engine** - Execute complex SQL queries with real-time results powered by DuckDB
- **DBT Integration** - One-click data transformations and quality testing
- **Table Browser** - Explore database schema and table relationships
- **Analytics Dashboard** - Monitor platform usage and pipeline health
- **Fast Performance** - Columnar analytics engine with vectorized operations

## Quick Start

### Prerequisites
- Python 3.8 or higher
- VS Code (recommended)
- pip package manager

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/queryverse-data-platform.git
cd queryverse-data-platform
```

2. **Open in VS Code**
```bash
code .
```

3. **Create virtual environment**
```bash
# In VS Code terminal (Ctrl+`)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python backend.py
```

6. **Open your browser**
```
http://localhost:8000/app
```

## Screenshots

### File Upload & Dataset Creation
![Upload Interface](screenshots/screenshot-2-upload.png)
*Easy drag-and-drop file upload with automatic table creation and robust CSV parsing*

![Create Dataset](screenshots/screenshot-3-create-dataset.png)
*Built-in dataset creator for manual data entry with spreadsheet-like interface*

### SQL Query Interface
![SQL Query](screenshots/screenshot-4-sql-query.png)
*Powerful SQL query editor with available tables sidebar*

![Query Results](screenshots/screenshot-5-results.png)
*Real-time query execution with formatted results table*

### Data Transformations
![DBT Transformations](screenshots/screenshot-6-dbt.png)
*One-click DBT-style transformations with detailed execution logs*

![Tables Browser](screenshots/screenshot-7-tables.png)
*Browse and explore all database tables with quick query options*

### Analytics & Monitoring
![Analytics Dashboard](screenshots/screenshot-8-analytics.png)
*Real-time analytics and data pipeline health monitoring*

## Architecture

QueryVerse uses a simple yet powerful architecture perfect for local development and prototyping:

- **Frontend**: Vanilla HTML/CSS/JavaScript (no build process required)
- **Backend**: FastAPI (Python) with async support
- **Database**: DuckDB embedded analytical database
- **Transformations**: SQL-based transformations (DBT-style)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│   FastAPI       │────│    DuckDB       │
│   (HTML/JS)     │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Why This Architecture?
- **No external database needed** - DuckDB runs embedded in Python
- **Fast analytics** - Columnar storage optimized for analytical queries
- **Simple deployment** - Everything runs in a single Python process
- **Full SQL support** - Complex joins, window functions, CTEs all work
- **No build tools** - Frontend works directly in browser

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | High-performance async API framework |
| **Database** | DuckDB | Embedded analytical database engine |
| **Frontend** | HTML/CSS/JS | Simple, fast web interface |
| **Data Processing** | Pandas | Data manipulation and CSV/Excel loading |
| **Transformations** | SQL | Direct SQL transformations on DuckDB |
| **Development** | VS Code | IDE with Python debugging support |

## Development in VS Code

### Recommended VS Code Extensions
- **Python** (Microsoft) - Essential for Python development
- **Pylance** (Microsoft) - Advanced Python language support
- **Python Debugger** (Microsoft) - Debugging support
- **SQLTools** (Matheus Teixeira) - SQL query assistance

### VS Code Features Used
- **Integrated Terminal** - Run the backend directly
- **Python Debugging** - Set breakpoints in backend.py
- **File Explorer** - Easy navigation between files
- **Git Integration** - Version control built-in

### Debug Configuration
Create `.vscode/launch.json` for debugging:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: QueryVerse Backend",
            "type": "python",
            "request": "launch",
            "program": "backend.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## Use Cases

- **Business Intelligence** - Quick data analysis and reporting for small teams
- **Data Exploration** - Interactive data discovery and ad-hoc querying
- **Prototyping** - Rapid development of data applications and dashboards
- **Education** - Learning SQL, data transformation concepts, and analytics
- **Personal Projects** - Analyze personal data, CSVs, spreadsheets
- **Small Business Analytics** - Sales analysis, customer insights, reporting

## Project Structure

```
queryverse-data-platform/
├── backend.py              # Main FastAPI application
├── frontend.html           # Complete web interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore            # Git ignore rules
├── screenshots/          # Documentation screenshots
├── uploads/              # Temporary upload directory (auto-created)
├── dbt_models/          # DBT model files (auto-created)
└── queryverse.db        # DuckDB database file (auto-created)
```

## Example Workflow

1. **Start the application** in VS Code terminal
2. **Upload a CSV file** (e.g., sales data, customer data)
3. **Browse tables** to see your uploaded data
4. **Write SQL queries** to analyze the data:
   ```sql
   SELECT department, COUNT(*) as employee_count, AVG(salary) as avg_salary
   FROM raw.employees 
   GROUP BY department 
   ORDER BY avg_salary DESC;
   ```
5. **Run DBT transformations** to create staging and mart tables
6. **View analytics** to monitor your data pipeline
7. **Create custom datasets** for testing and development

## Performance & Capabilities

### What QueryVerse Handles Well
- **Medium datasets** (up to 1GB CSV files)
- **Complex SQL queries** with joins and aggregations
- **Real-time query execution** (sub-second for most queries)
- **Multiple file formats** (CSV, Excel with robust parsing)
- **Data transformations** (staging, cleaning, business logic)

### Technical Specifications
- **Query Engine**: DuckDB (columnar, vectorized)
- **File Upload**: Multi-strategy CSV parsing for malformed files
- **Concurrent Users**: Single-user focused (perfect for development)
- **Memory Usage**: Efficient with columnar storage
- **Response Time**: <100ms for typical analytical queries

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** in VS Code
4. **Test locally** (`python backend.py`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comments for complex SQL transformations
- Test with various CSV file formats
- Update screenshots if UI changes are made

## Troubleshooting

### Common Issues

**Virtual environment not activated**
```bash
# You should see (venv) in your terminal prompt
# If not, activate it:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**Port 8000 already in use**
```bash
# Check what's using the port
netstat -an | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux

# Or change the port in backend.py
port = int(os.environ.get("PORT", 8001))  # Use 8001 instead
```

**CSV upload fails**
- The system handles malformed CSV files automatically
- Check the terminal for detailed parsing logs
- Large files (>100MB) may take longer to process

**SQL query errors**
- DuckDB uses standard SQL syntax
- Table names are case-sensitive
- Use schema.table format (e.g., `raw.my_data`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **FastAPI** for the excellent async web framework
- **DuckDB** for the powerful embedded analytics database
- **Pandas** for robust data manipulation capabilities
- **VS Code** for the outstanding development experience

⭐ **Happy analyzing!** Star this repository if you find QueryVerse useful for your data projects!
