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
if 'feeds' not in st.session_state:
    st.session_state['feeds'] = None

st.title("Agentic AI Logistics Optimization Dashboard")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Controls")
    if st.button("Run Optimization"):
        resp = requests.post(f"{BACKEND}/optimize", json={"source": 0, "target": 19})
        data = resp.json()
        st.session_state['initial_plan'] = data
        st.session_state['updated_plan'] = None
        st.session_state['event'] = None
        st.session_state['feeds'] = requests.get(f"{BACKEND}/feeds").json()
        st.success("Initial optimization complete")

    st.markdown("---")
    st.subheader("Simulate event")
    if st.button("Generate a random disruption"):
        resp = requests.post(f"{BACKEND}/simulate_event")
        result = resp.json()
        st.session_state['event'] = result.get('event')
        st.session_state['updated_plan'] = result.get('updated_plan')
        st.session_state['feeds'] = requests.get(f"{BACKEND}/feeds").json()
        st.success("Disruption simulated and route updated")

    st.markdown("---")
    st.subheader("Custom disruption")
    event_type = st.selectbox("Event type", ["traffic", "weather", "fuel"])
    edge_in = st.text_input("Edge for event (u,v)", value="(0,1)")
    severity = st.slider("Severity", 1.1, 3.5, 2.0)
    new_price = st.number_input("Fuel price ($/L)", value=1.8)
    if st.button("Inject custom disruption"):
        payload = {"type": event_type}
        if event_type in ["traffic", "weather"]:
            try:
                stripped = edge_in.strip().replace('(', '').replace(')', '')
                u_str, v_str = stripped.split(',')
                payload["edge"] = [int(u_str), int(v_str)]
            except Exception:
                st.error("Edge must be in format (0,1)")
                payload["edge"] = [0, 1]
            payload["severity"] = float(severity)
        else:
            payload["new_price"] = float(new_price)
        resp = requests.post(f"{BACKEND}/disrupt", json=payload)
        result = resp.json()
        st.session_state['event'] = result.get('event')
        st.session_state['updated_plan'] = result.get('updated_plan')
        st.session_state['feeds'] = requests.get(f"{BACKEND}/feeds").json()
        st.success("Custom disruption injected")

with col2:
    st.header("Fleet & Market Feed")
    if st.session_state['feeds']:
        st.json(st.session_state['feeds'])
    else:
        st.info("Run an optimization or simulate an event to fetch feed data.")

st.markdown("---")

st.header("Initial Route")
if st.session_state['initial_plan']:
    best = st.session_state['initial_plan'].get('best_plan', {})
    st.write(best.get('route'))
    st.subheader("Explanation")
    st.write(st.session_state['initial_plan'].get('explanation'))
    st.subheader("Initial Fleet Cost")
    st.json(best.get('cost', {}))
else:
    st.info("Press Run Optimization to compute the first route.")

st.markdown("---")

st.header("Updated Route")
if st.session_state['updated_plan']:
    best = st.session_state['updated_plan'].get('best_plan', {})
    st.write(best.get('route'))
    st.subheader("Explanation")
    st.write(st.session_state['updated_plan'].get('explanation'))
    st.subheader("Updated Fleet Cost")
    st.json(best.get('cost', {}))
else:
    st.info("Updated results will appear here after a disruption.")

st.markdown("---")

st.header("Cost Comparison")
if st.session_state['initial_plan'] and st.session_state['updated_plan']:
    initial_cost = st.session_state['initial_plan']['best_plan']['cost']['total_cost']
    updated_cost = st.session_state['updated_plan']['best_plan']['cost']['total_cost']
    diff = updated_cost - initial_cost
    st.metric("Initial Cost", f"${initial_cost:.2f}", delta=None)
    st.metric("Updated Cost", f"${updated_cost:.2f}", delta=f"${diff:.2f}")
    st.write("Multiple vehicles are scored and we choose the most cost-efficient route.")

st.markdown("---")

st.header("Disruption Event")
if st.session_state['event']:
    st.json(st.session_state['event'])
else:
    st.write("No disruption event has been applied yet.")

st.markdown("---")

st.header("Graph and Route Visualization")
resp = requests.get(f"{BACKEND}/graph")
if resp.status_code == 200:
    g = resp.json()
    nodes = g['nodes']
    edges = g['edges']
    node_lookup = {node['id']: node for node in nodes}
    fig = go.Figure()
    for edge in edges:
        x0, y0 = node_lookup[edge['u']]['pos']
        x1, y1 = node_lookup[edge['v']]['pos']
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(width=2, color='gray'),
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[node['pos'][0] for node in nodes],
            y=[node['pos'][1] for node in nodes],
            mode='markers+text',
            marker=dict(size=10, color='blue'),
            text=[node['name'] for node in nodes],
            textposition='top center',
            showlegend=False,
        )
    )

    def draw_route(route_path, color, name):
        if not route_path:
            return
        xs = [node_lookup[node]['pos'][0] for node in route_path]
        ys = [node_lookup[node]['pos'][1] for node in route_path]
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode='lines+markers',
                line=dict(width=4, color=color),
                marker=dict(size=8),
                name=name,
            )
        )

    if st.session_state['initial_plan']:
        draw_route(st.session_state['initial_plan']['best_plan']['route']['path'], 'green', 'Initial Route')
    if st.session_state['updated_plan']:
        draw_route(st.session_state['updated_plan']['best_plan']['route']['path'], 'red', 'Updated Route')

    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to fetch graph from backend")
