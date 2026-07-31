import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import simulate

st.set_page_config(page_title="AI Models - CarbonatiX", page_icon=":robot:", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

st.title("AI Simulation Engine")

st.subheader("What-If Simulation")

with st.form("simulate_form"):
    facility_id = st.text_input("Facility ID", key="sim_facility_id")

    st.write("### Simulation Parameters")
    shift_coal = st.slider(
        "Shift Coal to Hydro (%)",
        min_value=0,
        max_value=100,
        value=20,
        help="Percentage of coal energy to shift to hydroelectric power",
    )
    production_overdrive = st.slider(
        "Production Capacity Overdrive (%)",
        min_value=50,
        max_value=150,
        value=100,
        help="Production capacity as percentage of nominal",
    )
    ore_quality = st.slider(
        "Ore Quality (Moisture + Ni Grade %)",
        min_value=0,
        max_value=100,
        value=50,
        help="Combined ore quality metric",
    )
    inject_bio = st.checkbox(
        "Inject Bio Coke Reductant",
        value=False,
        help="Use biological coke as reductant in furnace",
    )

    if st.form_submit_button("Run Simulation"):
        if facility_id:
            with st.spinner("Running simulation..."):
                try:
                    result = simulate(
                        {
                            "facility_id": facility_id,
                            "shift_coal_to_hydro_pct": shift_coal,
                            "production_capacity_overdrive_pct": production_overdrive,
                            "ore_quality_moisture_ni_grade_pct": ore_quality,
                            "inject_bio_coke_reductant": inject_bio,
                        }
                    )

                    st.success("Simulation completed!")
                    st.divider()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Results")
                        if "current_emissions" in result:
                            st.metric(
                                "Current Emissions (tCO2)",
                                f"{result['current_emissions']:,.2f}",
                            )
                        if "projected_emissions" in result:
                            st.metric(
                                "Projected Emissions (tCO2)",
                                f"{result['projected_emissions']:,.2f}",
                            )
                        if "emissions_reduction" in result:
                            st.metric(
                                "Emissions Reduction (%)",
                                f"{result['emissions_reduction']:,.2f}%",
                            )

                    with col2:
                        st.subheader("Recommendations")
                        if "recommendations" in result:
                            for rec in result["recommendations"]:
                                st.write(f"- {rec}")
                        else:
                            st.info("No specific recommendations for this configuration.")

                    if "breakdown" in result:
                        st.subheader("Emissions Breakdown")
                        st.json(result["breakdown"])

                except Exception as e:
                    st.error(f"Simulation failed: {str(e)}")
        else:
            st.error("Please provide a Facility ID.")

st.divider()

st.subheader("Quick Presets")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Green Focus"):
        st.session_state.shift_coal = 80
        st.session_state.prod_od = 90
        st.session_state.ore_q = 60
        st.session_state.bio = True
        st.rerun()

with col2:
    if st.button("Balanced"):
        st.session_state.shift_coal = 40
        st.session_state.prod_od = 100
        st.session_state.ore_q = 50
        st.session_state.bio = False
        st.rerun()

with col3:
    if st.button("Max Production"):
        st.session_state.shift_coal = 10
        st.session_state.prod_od = 140
        st.session_state.ore_q = 40
        st.session_state.bio = False
        st.rerun()
