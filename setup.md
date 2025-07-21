# QueryVerse - Simplified Setup (4 Main Files)

## Project Structure (Minimal)
```
queryverse/
├── backend.py              # Complete backend (FastAPI + DBT)
├── frontend.html           # Complete frontend (HTML + React CDN)
├── requirements.txt        # Python dependencies
└── README.md               # Setup instructions
```

## 🚀 Quick Setup (5 Minutes!)

```bash
# 1. Create project
mkdir queryverse && cd queryverse

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn pandas duckdb dbt-core dbt-duckdb python-multipart aiofiles sqlparse pyyaml

# 4. Download the 4 files into this directory:
#    - backend.py
#    - frontend.html  
#    - requirements.txt
#    - README.md

# 5. Run the application
python backend.py
```

**Then open your browser to: http://localhost:8000/app**

## ✨ What You Get:

- ✅ **File Upload**: Drag & drop CSV/Excel files
- ✅ **Auto DBT Models**: Staging models created automatically  
- ✅ **SQL Query Editor**: Execute custom queries with syntax highlighting
- ✅ **Data Visualization**: Auto-generated charts from query results
- ✅ **DBT Integration**: Run, test, and generate docs
- ✅ **Table Browser**: Explore all your data tables
- ✅ **Analytics Dashboard**: Platform usage statistics
- ✅ **Real-time Notifications**: Success/error messages

## 📊 Complete Data Flow:

1. **Upload** → `raw.table_name` created in DuckDB
2. **DBT Run** → Staging models transform data  
3. **SQL Query** → Query any table with custom SQL
4. **Visualize** → Auto-generated charts + data tables
5. **Monitor** → Analytics dashboard shows pipeline health

## 🔥 Benefits of This Approach:

- **4 files only** - Super simple to understand and modify
- **No build process** - Just run `python backend.py`
- **No Docker required** - Works on any machine with Python
- **Production ready** - Can still be deployed to cloud
- **Full functionality** - Same features as complex multi-file setup
- **Easy debugging** - Everything in one place

## 🚀 Production Deployment:

```bash
# For production, just:
pip install gunicorn
gunicorn backend:app --host 0.0.0.0 --port 8000
```

Or deploy to:
- **Heroku**: Push these 4 files
- **Railway**: Connect GitHub repo  
- **Render**: Auto-deploy from GitHub
- **Google Cloud Run**: Use Cloud Build
- **AWS Lambda**: With Mangum wrapper

## 💡 Extension Ideas:

Since everything is in single files, it's easy to:
- Add new API endpoints in `backend.py`
- Add new UI components in `frontend.html`
- Customize DBT models in the code
- Add authentication, file storage, etc.

## 🆚 vs Multi-File Setup:

| Aspect | Simplified (4 files) | Multi-File |
|--------|---------------------|------------|
| Setup Time | 5 minutes | 30+ minutes |
| Files to Manage | 4 | 20+ |
| Build Process | None | Complex |
| Dependencies | Python only | Node.js + Python |
| Debugging | Easy | Complex |
| Functionality | 100% same | 100% same |

**Perfect for**: Learning, prototyping, demos, small teams, quick deployment