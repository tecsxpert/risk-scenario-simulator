
AI Risk SCENARIO SIMULATOR


## Architecture


User → Flask API → Redis (Cache) → Groq AI
↓
Async Processing


##  Workflow

1. User sends request to `/query`
2. System checks Redis cache
3. If not found → calls Groq AI
4. AI generates response
5. Response stored in cache
6. Result returned to user


##  How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Create `.env` file

```
GROQ_API_KEY=your_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379

### 3. Run the app
python app.py

## Testing

### Health
http://127.0.0.1:5000/health

### Query (PowerShell)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/query -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"question":"cyber attack risk"}'


## Demo Steps

1. Run server
2. Show `/health`
3. Run `/query`
4. Run same query again (show caching)
5. Run `/generate-report`
6. Show `/report-status`

---

##  Author

**Harshitha Umesh**

GitHub:
[https://github.com/Harshitha-umesh/risk-scenario-simulator](https://github.com/Harshitha-umesh/risk-scenario-simulator)
