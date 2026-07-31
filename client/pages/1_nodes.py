import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import get_nodes, get_node_parameters, create_node_parameter

st.set_page_config(page_title="Nodes - CarbonatiX", page_icon=":electric_plug:", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

st.title("Node Monitoring Dashboard")

st.sidebar.header("Filters")
facility_filter = st.sidebar.text_input("Facility ID", key="node_facility_filter")
status_filter = st.sidebar.selectbox("Status", ["", "active", "idle", "maintenance"], key="node_status_filter")
node_type_filter = st.sidebar.selectbox("Node Type", ["", "furnace", "converter", "casting"], key="node_type_filter")
page = st.sidebar.number_input("Page", min_value=1, value=1, key="node_page")

params = {"page": page, "page_size": 20}
if facility_filter:
    params["facility_id"] = facility_filter
if status_filter:
    params["status"] = status_filter
if node_type_filter:
    params["node_type"] = node_type_filter

try:
    nodes_data = get_nodes(params)
    nodes = nodes_data.get("items", [])
    total = nodes_data.get("total", len(nodes))
    st.write(f"**{total}** nodes found")

    if nodes:
        for node in nodes:
            with st.expander(f"{node.get('node_name', 'Unknown')} ({node.get('node_id', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Facility:** {node.get('facility_id', 'N/A')}")
                    st.write(f"**Line:** {node.get('line', 'N/A')}")
                    st.write(f"**Type:** {node.get('node_type', 'N/A')}")
                    st.write(f"**Status:** {node.get('status', 'N/A')}")
                with col2:
                    st.write(f"**Latitude:** {node.get('latitude', 'N/A')}")
                    st.write(f"**Longitude:** {node.get('longitude', 'N/A')}")

                st.subheader("Parameter History")
                try:
                    params_data = get_node_parameters(node["node_id"])
                    parameters = params_data.get("items", [])
                    if parameters:
                        st.dataframe(parameters, use_container_width=True)
                    else:
                        st.info("No parameters recorded yet.")
                except Exception as e:
                    st.error(f"Failed to load parameters: {str(e)}")

                with st.form(f"add_param_{node['node_id']}"):
                    st.write("Add Parameter")
                    electrode_load = st.number_input("Electrode Load", key=f"el_{node['node_id']}")
                    tap_temp = st.number_input("Tap Temperature", key=f"tt_{node['node_id']}")
                    power_draw = st.number_input("Power Draw", key=f"pd_{node['node_id']}")
                    emissions = st.number_input("Hourly Emissions", key=f"em_{node['node_id']}")

                    if st.form_submit_button("Submit"):
                        try:
                            from datetime import datetime, timezone
                            create_node_parameter(
                                node["node_id"],
                                {
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "electrode_load": electrode_load,
                                    "tap_temperature": tap_temp,
                                    "power_draw": power_draw,
                                    "hourly_emissions": emissions,
                                },
                            )
                            st.success("Parameter added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add parameter: {str(e)}")
    else:
        st.info("No nodes found.")
except Exception as e:
    st.error(f"Failed to load nodes: {str(e)}")
