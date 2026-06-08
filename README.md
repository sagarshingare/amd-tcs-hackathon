# Agentic AI Logistics Optimization System

## 🚀 What This System Does (In Simple Terms)

Imagine you're a delivery company with multiple trucks. You need to get packages from point A to point B, but the route keeps changing due to traffic, weather, and fuel prices. This system **automatically finds the best route, picks the right vehicle, and explains why it chose that option** — all in real-time.

---

## 📊 The Problem It Solves

**Without this system:**
- Drivers manually plan routes (slow, inefficient)
- Traffic accidents cause delays and wasted fuel
- Fuel price spikes aren't factored into decisions
- Nobody knows *why* a route was chosen
- No tracking of delivery carbon emissions

**With this system:**
- Routes are auto-optimized using AI agents
- Real-time disruptions (traffic, weather) are detected and adapted to
- Fuel costs and prices are considered automatically
- Every decision is explained in plain English
- Carbon emissions are calculated for sustainability tracking

---

## 🎯 How It Works (End-to-End)

### Step 1: You Input a Delivery Request
```
From: Warehouse (Location 0)
To: Customer Store (Location 19)
```

### Step 2: The System Analyzes Everything
- **Routing Agent** finds the shortest path through the city
- **Cost Agent** calculates fuel costs, vehicle efficiency, and overhead
- **Monitoring Agent** checks for real-time disruptions (traffic, weather)
- **Decision Agent** compares all vehicles (van, truck, hybrid) and picks the best one

### Step 3: You See the Results in a Dashboard
- 📍 **Initial Route**: Original best path with costs
- 🔄 **Updated Route**: Adjusted path if disruptions are detected
- 💰 **Cost Comparison**: See why one route/vehicle is cheaper
- 🛣️ **Map View**: Visual overlay of initial (green) vs updated (red) routes
- 📝 **AI Explanation**: Human-readable explanation of decisions

### Step 4: Test "What-If" Scenarios
- Simulate a traffic accident on a key road
- Weather events that slow travel
- Fuel price spikes
- See how the system adapts in real-time

---

## 🏗️ System Architecture (Simplified)

```
┌─────────────────────────────────────────────────────┐
│  You (Streamlit Dashboard in Browser)               │
│  • Input: Start point, End point                     │
│  • View: Routes, costs, maps, explanations           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Backend AI System (FastAPI)                         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Decision Agent (The Boss)                     │  │
│  │ • Says "use truck on Route A because..."     │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│      ┌──────────────┼──────────────┬──────────────┐ │
│      ▼              ▼              ▼              ▼ │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌──────┐ │
│  │Routing │    │ Cost   │    │Traffic │    │ Real │ │
│  │Agent   │    │ Agent  │    │Disrupt │    │Time  │ │
│  │(Maps)  │    │(Money) │    │(Traffic)    │Data │ │
│  └────────┘    └────────┘    └────────┘    └──────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Installation (3 Steps)

### Step 1: Setup Python Environment
```bash
# Navigate to project folder
cd /Users/sagarshingare/amd-tcs-hackathon

# Create isolated Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Start the Backend (AI Engine)
```bash
# Option A: Using script (automatic)
./scripts/run_backend.sh

# Option B: Manual start
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
You should see: `✓ Uvicorn running on http://127.0.0.1:8000`

### Step 3: Start the Dashboard (Frontend)
```bash
# In a NEW terminal, with venv activated
streamlit run frontend/app.py
```
A browser window opens automatically at `http://localhost:8501`

---

## 🎮 How to Use It

### 1. **Run Optimization** (Main Button)
- Picks a start point (warehouse) and end point (customer)
- Shows initial route and AI's recommended vehicle
- Displays cost breakdown (fuel, overhead, profit)
- Shows carbon emissions

### 2. **See Real-Time Disruptions**
- Click `Generate Random Disruption` to simulate:
  - 🚨 Traffic jam (slows route, increases time)
  - ☔ Bad weather (increases travel time)
  - ⛽ Fuel price spike (increases cost)
- Watch the system adapt: route changes, vehicle might change, costs recalculate

### 3. **Test "What-If" Scenarios**
- Manually inject a traffic delay on specific road
- Manually adjust fuel prices
- See updated recommendations instantly

### 4. **View the Map**
- Green path = original route
- Red path = updated route (after disruption)
- Hover for details (distance, time, cost)

### 5. **Read AI Explanation**
- System explains *why* it chose a route
- Example: _"Updated route due to traffic on Road A. Truck is 15% cheaper than van."_

---

## 🎁 Bonus Features Included

### ✅ Multi-Vehicle Support
- **Van**: Cheap, small (good for light packages)
- **Truck**: Expensive, big capacity (good for heavy loads)
- **Hybrid**: Mid-range, balanced efficiency

System auto-picks best vehicle based on cost

### ✅ Carbon Emissions Tracking
- Every route shows CO2 footprint
- Helps track sustainability goals
- Vans emit less than trucks

### ✅ Real-Time Data Integration
- System can connect to live traffic APIs (Google Maps, TomTom)
- Can fetch real weather from OpenWeatherMap
- Can get fuel prices from energy agencies
- Currently uses mock data for demo

### ✅ Smart Cost Calculation
- Factors in: fuel consumption, vehicle efficiency, labor time, profit margin
- Updates automatically when fuel prices change
- Shows breakdown so you understand costs

---

## 📁 What's Inside (File Structure)

```
amd-tcs-hackathon/
├── backend/                          # AI Engine (brain)
│   ├── agents/
│   │   ├── routing_agent.py           # Map navigation (finds shortest path)
│   │   ├── cost_agent.py              # Cost calculator (fuel, time, profit)
│   │   ├── disruption_agent.py        # Detects traffic, weather, fuel changes
│   │   ├── monitoring_agent.py        # Simulates real-world events
│   │   ├── decision_agent.py          # Main coordinator (decides best option)
│   │   └── external_api_agent.py      # Connects to real-time data sources
│   ├── data/
│   │   └── sample_data.py             # Creates practice city map with 20 locations
│   └── main.py                        # REST API server
├── frontend/
│   └── app.py                         # Dashboard (what you see in browser)
├── scripts/
│   ├── run_backend.sh                 # Start button for backend
│   └── run_frontend.sh                # Start button for frontend
├── requirements.txt                   # List of all Python libraries needed
└── REALTIME_DATA_INTEGRATION.md       # Guide for connecting real APIs

```

---

## 🚀 Quick Start (Copy-Paste)

```bash
# 1. Enter project folder
cd /Users/sagarshingare/amd-tcs-hackathon

# 2. Activate environment
source .venv/bin/activate

# 3. Terminal 1: Start backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# 4. Terminal 2: Start frontend
streamlit run frontend/app.py

# Browser opens → Click "Run Optimization" → See results!
```

---

## 🧪 Testing the System

### Test 1: Basic Route (5 min)
1. Click "Run Optimization"
2. Wait for route to appear
3. Click "Show Map Visualization"
4. See green path on map

### Test 2: Traffic Impact (5 min)
1. Click "Generate Random Disruption"
2. Wait 2 seconds
3. See red path (new route)
4. Compare costs: did it go up?

### Test 3: Custom Disruption (3 min)
1. Click "Inject Custom Traffic Delay"
2. Set severity slider to high
3. Click apply
4. See route change, cost change, vehicle might change

### Test 4: Understanding Decisions (2 min)
1. Scroll down to "AI Explanation"
2. Read why the vehicle was chosen
3. Try different disruptions, read different explanations

---

## 🔧 How to Customize

### Change City Map
Edit `backend/data/sample_data.py` to create different city layouts:
```python
# Currently: 4x5 grid (20 locations)
# Can change to: 5x6 grid (30 locations), random points, or real city
```

### Add New Vehicles
Edit `backend/main.py` fleet definition:
```python
# Add a new vehicle type with different cost model
```

### Connect Real APIs
Follow `REALTIME_DATA_INTEGRATION.md`:
1. Get free API keys (Google Maps, OpenWeatherMap, etc.)
2. Update `external_api_agent.py` with real endpoints
3. System automatically uses live traffic, weather, fuel data

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Port 8000 already in use" | Kill old process: `lsof -i :8000 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9` |
| "Streamlit not found" | Make sure `.venv` is activated: `source .venv/bin/activate` |
| "No module named X" | Reinstall: `pip install -r requirements.txt` |
| "Dashboard won't load" | Check backend is running: `curl http://127.0.0.1:8000/status` |
| "Map doesn't show" | Clear browser cache or try incognito mode |

---

## 🎓 What You're Learning

This project teaches:
- **Multi-agent systems**: How independent AI agents work together
- **Real-time optimization**: Adapting plans when conditions change
- **REST APIs**: Communication between frontend & backend
- **Graph algorithms**: Finding best paths in networks
- **Cost modeling**: Factoring multiple variables into decisions
- **Data visualization**: Making complex data understandable

---

## 🏆 Why This Matters for Hackathons

✅ **Complete working system** (not just prototype)
✅ **Real AI agents** (not just if-then rules)
✅ **Beautiful dashboard** (judges will like UI)
✅ **Explainable AI** (judges will understand decisions)
✅ **Scalable architecture** (can add more features)
✅ **Production-ready code** (proper error handling, async)

---

## 📞 Need Help?

1. **Code not running?** → Check `backend/main.py` compiles: `python3 -m py_compile backend/main.py`
2. **Dashboard empty?** → Check backend logs in Terminal 1
3. **Routes not showing?** → Check `frontend/app.py` for error messages
4. **Want to integrate real data?** → See `REALTIME_DATA_INTEGRATION.md`

---

## 🎉 You're Ready!

Your logistics optimization system is ready to:
- Find best routes automatically
- Save money on fuel
- Adapt to real-world disruptions
- Make data-driven decisions
- Track sustainability

**Next step**: Click "Run Optimization" and see the magic happen! 🚀
