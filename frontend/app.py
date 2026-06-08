import os
import streamlit as st
import requests
import plotly.graph_objects as go

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Logistics Dashboard", layout="wide")

if 'initial_plan' not in st.session_state:
    st.session_state['initial_plan'] = None
if 'updated_plan' not in st.session_state:
    st.session_state['updated_plan'] = None
if 'event' not in st.session_state:
    st.session_state['event'] = None

st.title("Agentic AI Logistics Optimization Dashboard")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Controls")
    if st.button("Run Optimization"):
        resp = requests.post(f"{BACKEND}/optimize", json={"source": 0, "target": 1})
        data = resp.json()
        st.session_state['plan'] = data
        st.session_state['initial_plan'] = data
        st.session_state['updated_plan'] = None
        st.session_state['event'] = None
        st.success("Optimization complete")

    st.markdown("---")
    st.subheader("Inject Disruption")
    dtype = st.selectbox("Type", ["traffic", "fuel"])
    if dtype == 'traffic':
        edge_in = st.text_input("Edge (u,v)", value="(0,1)")
        severity = st.slider("Severity", 1.1, 5.0, 2.0)
        if st.button("Inject Traffic Disruption"):
            try:
                stripped = edge_in.strip().replace('(', '').replace(')', '')
                u_str, v_str = stripped.split(',')
                u, v = int(u_str), int(v_str)
            except Exception:
                st.error("Edge must be like (0,1)")
                u, v = 0, 1
            resp = requests.post(f"{BACKEND}/disrupt", json={"type": "traffic", "edge": [u, v], "severity": float(severity)})
            result = resp.json()
            st.session_state['event'] = result.get('event')
            st.session_state['updated_plan'] = result.get('updated_plan')
            st.session_state['plan'] = result.get('updated_plan')
            st.success("Traffic disruption injected and route updated")
    else:
        new_price = st.number_input("New fuel price ($/L)", value=1.8)
        if st.button("Inject Fuel Price Change"):
            resp = requests.post(f"{BACKEND}/disrupt", json={"type": "fuel", "new_price": float(new_price)})
            result = resp.json()
            st.session_state['event'] = result.get('event')
            st.session_state['updated_plan'] = result.get('updated_plan')
            st.session_state['plan'] = result.get('updated_plan')
            st.success("Fuel price change injected and route updated")

with col2:
    st.header("Status")
    if st.session_state.get('initial_plan'):
        st.subheader("Initial Route Explanation")
        st.write(st.session_state['initial_plan'].get('explanation'))
        st.subheader("Initial Cost")
        st.json(st.session_state['initial_plan'].get('cost'))
    else:
        st.info("Run optimization to generate an initial route")
    if st.session_state.get('updated_plan'):
        st.subheader("Updated Route Explanation")
        st.write(st.session_state['updated_plan'].get('explanation'))
        st.subheader("Updated Cost")
        st.json(st.session_state['updated_plan'].get('cost'))
    if st.session_state.get('initial_plan') and st.session_state.get('updated_plan'):
        st.subheader("Cost Comparison")
        initial_cost = st.session_state['initial_plan']['cost']['total_cost']
        updated_cost = st.session_state['updated_plan']['cost']['total_cost']
        diff = updated_cost - initial_cost
        st.metric("Initial Cost", f"${initial_cost:.2f}", delta=None)
        st.metric("Updated Cost", f"${updated_cost:.2f}", delta=f"${diff:.2f}")
    elif st.session_state.get('updated_plan'):
        st.info("Updated route is available after disruption")

st.markdown("---")

st.header("Graph Visualization")
resp = requests.get(f"{BACKEND}/graph")
if resp.status_code == 200:
    g = resp.json()
    nodes = g['nodes']
    edges = g['edges']
    xs = [n['pos'][0] for n in nodes]
    ys = [n['pos'][1] for n in nodes]
    fig = go.Figure()
    for e in edges:
        u = e['u']
        v = e['v']
        x0, y0 = nodes[u]['pos']
        x1, y1 = nodes[v]['pos']
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(width=2, color='gray'), showlegend=False))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text', marker=dict(size=12, color='blue'), text=[n['id'] for n in nodes], textposition='top center'))

    # Overlay route if exists
    plan = st.session_state.get('plan')
    if plan and plan.get('route'):
        rt = plan['route']['path']
        rx = [nodes[n]['pos'][0] for n in rt]
        ry = [nodes[n]['pos'][1] for n in rt]
        fig.add_trace(go.Scatter(x=rx, y=ry, mode='lines+markers', line=dict(width=4, color='red'), marker=dict(size=8, color='red'), name='route'))

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to fetch graph from backend")

st.markdown("---")
st.header("Latest Event")
if 'event' in st.session_state:
    st.json(st.session_state['event'])
else:
    st.write("No events injected yet")
