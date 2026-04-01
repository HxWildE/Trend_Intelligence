# Fast-Track Run Guide (Local Environment)

This guide takes you straight into running the **Trend Intelligence System** on your local machine, where everything (Python, Node.js, Docker, virtual environments) is already installed and set up.

You will need **5 separate terminals** running continuously. All commands assume you start exactly at the project root directory: `C:\Users\himan\Desktop\trend-intelligence-system`.

---

## 🏗️ Terminal 1: Start Infrastructure (Docker)
This terminal boots PostgreSQL, Redis, and the Nginx API Gateway.

1. Open Terminal 1.
2. Run the command:
   ```cmd
   docker-compose up -d
   ```
*(You can close or reuse this terminal after the command finishes, as `-d` runs the containers in the background. Use `docker ps` to verify 3 containers are running.)*

---

## 🔄 Terminal 2: Data Pipeline (Scheduler)
This terminal runs the ETL pipelines (Reddit scraping + DB loading) every hour.

1. Open Terminal 2.
2. Activate the virtual environment:
   ```cmd
   .\venv\Scripts\activate
   ```
3. Boot the scheduler:
   ```cmd
   python data_pipeline\schedulers\cron_jobs.py
   ```
*(Leave this terminal running!)*

---

## 🤖 Terminal 3: Machine Learning Background Worker
This terminal constantly listens to Redis for heavy Machine Learning tasks (Clustering, NLP Sentiment, Embeddings) requested by the frontend to prevent UI freezing.

1. Open Terminal 3.
2. Activate the virtual environment:
   ```cmd
   .\venv\Scripts\activate
   ```
3. Start the Background Worker:
   ```cmd
   python backend\worker.py
   ```
*(Leave this terminal running!)*

---

## 🌐 Terminal 4: FastAPI Backend Server
This terminal hosts the core ASGI backend server.

1. Open Terminal 4.
2. Activate the virtual environment:
   ```cmd
   .\venv\Scripts\activate
   ```
3. Run the Uvicorn server:
   ```cmd
   uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
   ```
*(Leave this terminal running! You can visit `http://127.0.0.1:8000/docs` to see the API swagger page.)*

---

## 🎨 Terminal 5: React Frontend
This terminal spins up the user interface.

1. Open Terminal 5.
2. Move into the frontend folder:
   ```cmd
   cd frontend
   ```
3. Start the Vite dev server:
   ```cmd
   npm run dev
   ```
*(Leave this terminal running!)*

---

### 🎉 You're Done!
Go to [http://localhost:5173/](http://localhost:5173/) in your web browser. 
The system is fully connected and ready to process live dynamic global trend data!

### Shutting Down
When you are completely done:
1. `Ctrl+C` in Terminals 2, 3, 4, and 5.
2. In Terminal 1 (or any new terminal at the root directory), run:
   ```cmd
   docker-compose down
   ```
This gracefully shuts down the databases and cache.
