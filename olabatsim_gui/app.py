import os

import numpy as np
import olabatsim as obs
import pandas as pd
import plotly.graph_objects as go
import pybamm
import streamlit as st
from olabatsim import PostProcessor  # Replace with your actual module
from plotly.subplots import make_subplots
from streamlit_progress import StreamlitHandler

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.set_page_config(layout="wide")
st.title("Cell Simulation GUI")

bat_opts = pybamm.BatteryModelOptions(None)
# Sidebar configuration form
with st.sidebar.form("config_form"):
    st.subheader("Simulation Configuration")
    model_type = st.selectbox("Select Model", ["SPMe", "DFN"])
    sei_option1 = st.selectbox("SEI Mode", bat_opts.possible_options["SEI"])
    sei_option2 = st.selectbox(
        "SEI porosity change", bat_opts.possible_options["SEI porosity change"]
    )
    sei_option3 = st.selectbox(
        "SEI on cracks", bat_opts.possible_options["SEI on cracks"]
    )

    thermal_option = st.selectbox("Thermal Mode", bat_opts.possible_options["thermal"])
    vehicle_model = st.selectbox("Vehicle Model", ["S1 Pro", "S1"])
    cell_model = st.selectbox("Cell Model", ["LG"])
    st.subheader("Solver Options (Casadi)")
    solver_mode = st.selectbox(
        "solver mode", ["safe", "fast", "fast with events", "safe without grid"]
    )
    dt_max = st.text_input("dt_max", "5")
    rtol = st.text_input("relative tolerance", "1e-6")
    atol = st.text_input("absolute tolerance", "1e-6")
    root_tol = st.text_input("root finding tolerance", "1e-6")
    max_step_decrease_count = st.text_input("maximum step decrease count", "5")
    integrators_maxcount = st.text_input("maximum number of integrators", "100")
    submit_config = st.form_submit_button("Apply Configuration")
    if submit_config:
        st.session_state.clear()
        st.success("Configuration applied. Please upload CSV file to proceed.")

# Use session_state to cache simulator and feasibility figure
if "uploaded_filename" not in st.session_state:
    st.session_state["uploaded_filename"] = None
if "dsim" not in st.session_state:
    st.session_state["dsim"] = None
if "feasibility_fig" not in st.session_state:
    st.session_state["feasibility_fig"] = None
if "info" not in st.session_state:
    st.session_state["info"] = None


def edit_solver_settings(solver_settings_df):
    # Convert edited values to correct types
    edited_solver_settings = {}
    for param, value in zip(
        solver_settings_df["Parameter"], solver_settings_df["Value"]
    ):
        type(solver_settings_df)
        if param in ["dt_max"]:
            edited_solver_settings[param] = float(value)
        elif param in ["atol", "rtol"]:
            edited_solver_settings[param] = float(value)
        elif param == "mode":
            edited_solver_settings[param] = str(value)
        else:
            edited_solver_settings[param] = value
    return edited_solver_settings


# Tabs for plots
tabs = st.tabs(["Simulation Plot", "Postprocessing"])
with tabs[0]:
    # Define the model based on user selection
    ModelClass = (
        pybamm.lithium_ion.SPMe if model_type == "SPMe" else pybamm.lithium_ion.DFN
    )
    options = {
        "SEI": sei_option1,
        "SEI porosity change": sei_option2,
        "SEI on cracks": sei_option3,
        "thermal": thermal_option,
    }
    # Additional degradation options
    add_deg_options = st.checkbox("Enable additional degradation options")
    if add_deg_options:
        st.sidebar.subheader("Degradation Mechanism Options")
        li_plating_option1 = st.sidebar.selectbox(
            "Lithium plating", bat_opts.possible_options["lithium plating"]
        )
        li_plating_option2 = st.sidebar.selectbox(
            "Lithium plating porosity change",
            bat_opts.possible_options["lithium plating porosity change"],
        )
        particle_mechanics_option = st.sidebar.selectbox(
            "Particle Mechanics", bat_opts.possible_options["particle mechanics"]
        )
        lam_option = st.sidebar.selectbox(
            "Loss of active material",
            bat_opts.possible_options["loss of active material"],
        )
    else:
        li_plating_option1 = None
        li_plating_option2 = None
        particle_mechanics_option = None
        lam_option = None
    if add_deg_options:
        options.update(
            {
                "lithium plating": li_plating_option1,
                "lithium plating porosity change": li_plating_option2,
                "particle mechanics": particle_mechanics_option,
                "loss of active material": lam_option,
            }
        )
    model = ModelClass(options=options, name="User Model")
    # Add an "eye" button to view model LaTeX in a popup
    with st.popover("View Model Equations", icon="👁️"):
        st.markdown(f""" $$ {model.latexify()} $$""")
    uploaded_file = st.file_uploader("Upload Drive Cycle CSV", type="csv")

    if uploaded_file:
        filepath = "temp_uploaded.csv"
        # Only process if file is new or changed
        if uploaded_file.name != st.session_state["uploaded_filename"]:
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Instantiate simulator
            dsim = obs.DriveCycleSimulator(
                filepath=filepath,
                model=model,
                vehicle_model=vehicle_model,
                cell_model=cell_model,
            )
            # Extract data with spinner
            dsim.extract_data(
                progress_handler=StreamlitHandler("Processing daywise data")
            )
            fig, info = dsim.check_data_feasibility(info=True)

            # Cache in session_state
            st.session_state["uploaded_filename"] = uploaded_file.name
            st.session_state["dsim"] = dsim
            st.session_state["feasibility_fig"] = fig
            st.session_state["info"] = info

        else:
            dsim = st.session_state["dsim"]
            fig = st.session_state["feasibility_fig"]
            info = st.session_state["info"]
        # Feasibility check
        st.subheader("Check Data Feasibility")
        with st.spinner("Checking feasibility..."):
            with st.popover("ℹ️"):
                st.text(info)

            if st.button("Plot Data Quality", use_container_width=True):
                st.pyplot(fig)
        # Advanced Solver Settings
        edited_solver_settings = dsim.solver_settings
        edited_sei_settings = dsim.sei_parameters
        edited_operating_settings = dsim.operating_conditions
        edited_thermal_settings = dsim.thermal_parameters
        dsim.rtol = rtol
        dsim.mode = solver_mode
        dsim.atol = atol
        dsim.dt_max = dt_max
        dsim.root_tol = root_tol
        dsim.max_step_decrease_count = max_step_decrease_count
        dsim.integrators_maxcount = integrators_maxcount

        # sei parameters
        if st.checkbox("SEI parameters"):
            st.subheader("SEI parameters")
            default_sei_settings = dsim.sei_parameters
            # Show editable table for solver settings
            sei_settings_df = st.data_editor(
                {
                    "Parameter": list(default_sei_settings.keys()),
                    "Value": list(default_sei_settings.values()),
                },
                num_rows="dynamic",
                use_container_width=True,
                key="sei_settings_editor",
            )
            print(sei_settings_df)
            for key, value in sei_settings_df.items():
                print("key : ", type(value))
            edited_sei_settings = {
                sei_settings_df["Parameter"][i]: float(sei_settings_df["Value"][i])
                for i in range(len(sei_settings_df["Parameter"]))
            }
        if st.checkbox("Operating Conditions"):
            st.subheader("Operating conditions")
            default_operating_settings = dsim.operating_conditions
            # Show editable table for solver settings
            operating_settings_df = st.data_editor(
                {
                    "Parameter": list(default_operating_settings.keys()),
                    "Value": list(default_operating_settings.values()),
                },
                num_rows="dynamic",
                use_container_width=True,
                key="operating_settings_editor",
            )
            edited_operating_settings = {
                operating_settings_df["Parameter"][i]: float(
                    operating_settings_df["Value"][i]
                )
                for i in range(len(operating_settings_df["Parameter"]))
            }

        if st.checkbox("Thermal Parameters"):
            st.subheader("Thermal Parameters")
            default_thermal_settings = dsim.thermal_parameters
            # Show editable table for solver settings
            thermal_settings_df = st.data_editor(
                {
                    "Parameter": list(default_thermal_settings.keys()),
                    "Value": list(default_thermal_settings.values()),
                },
                num_rows="dynamic",
                use_container_width=True,
                key="thermal_settings_editor",
            )
            edited_thermal_settings = {
                thermal_settings_df["Parameter"][i]: float(
                    thermal_settings_df["Value"][i]
                )
                for i in range(len(thermal_settings_df["Parameter"]))
            }

        # Apply the settings
        if st.button("Apply Settings"):
            # Convert edited values to correct types
            dsim.solver_settings = edited_solver_settings
            dsim.sei_parameters = edited_sei_settings
            dsim.operating_conditions = edited_operating_settings
            dsim.thermal_parameters = edited_thermal_settings
            st.success("Settings updated!")

        # Solver
        save_summary = st.checkbox("Save summary data", value=True)
        save_full_data = st.checkbox("Save full data", value=False)

        sim_days = st.text_input("Enter number of days to simulate")

        # Add a stop flag to session state
        if "stop_simulation" not in st.session_state:
            st.session_state["stop_simulation"] = False

        def stop_simulation_callback():
            st.session_state["stop_simulation"] = True

        col1, col2 = st.columns([2, 1])
        with col1:
            run_clicked = st.button("Run Simulation")
        with col2:
            stop_clicked = st.button(
                "Stop Simulation", on_click=stop_simulation_callback
            )

        if run_clicked:
            st.session_state["stop_simulation"] = False  # Reset stop flag
            with st.spinner("Running simulation..."):
                dsim = dsim

                def progress_handler(*args, **kwargs):
                    if st.session_state.get("stop_simulation", False):
                        raise RuntimeError("Simulation stopped by user.")
                    return StreamlitHandler("Simulating daywise data")

                try:
                    dsim.solve(
                        sim_days=int(sim_days),
                        progress_handler=progress_handler(),
                        save_full_data=save_full_data,
                        save_summary=save_summary,
                    )
                    rdf = pd.DataFrame(
                        {
                            "days": np.arange(1, len(dsim._Capacity_sim_all) + 1, 1),
                            "soh": np.array(dsim._Capacity_sim_all)
                            / dsim.parameter_values["Nominal cell capacity [A.h]"],
                            "max voltage": dsim._Max_Voltage_daywise,
                            "min voltage": dsim._Min_Voltage_daywise,
                        }
                    )
                    rdf.to_csv("./sim_data/simulation_results.csv", index=False)
                    st.success("Simulation completed!")
                except RuntimeError as e:
                    st.warning(str(e))
        if st.button("Plot results"):
            if os.path.exists("./sim_data/simulation_results.csv"):
                st.subheader("Simulation Results")
                rdf = pd.read_csv("./sim_data/simulation_results.csv")
                fig = make_subplots(
                    rows=1,
                    cols=2,
                    subplot_titles=(
                        f"Simulated SOH {rdf['days'].iloc[-1]} days",
                        "Max Voltage and Min Voltage",
                    ),
                    x_title="Time (days)",
                    horizontal_spacing=0.15,
                )

                # SOH plot
                fig.add_trace(
                    go.Scatter(
                        x=rdf["days"],
                        y=rdf["soh"],
                        mode="markers+lines",
                        marker=dict(color="blue", symbol="star"),
                        name="Simulation SoH",
                    ),
                    row=1,
                    col=1,
                )

                # Voltage plot
                fig.add_trace(
                    go.Scatter(
                        x=rdf["days"],
                        y=rdf["max voltage"],
                        mode="lines+markers",
                        name="Day's max voltage",
                        marker=dict(color="red"),
                    ),
                    row=1,
                    col=2,
                )
                fig.add_trace(
                    go.Scatter(
                        x=rdf["days"],
                        y=rdf["min voltage"],
                        mode="lines+markers",
                        name="Day's min voltage",
                        marker=dict(color="green"),
                    ),
                    row=1,
                    col=2,
                )

                fig.update_xaxes(title_text="Time (days)", row=1, col=1)
                fig.update_xaxes(title_text="Time (days)", row=1, col=2)
                fig.update_yaxes(title_text="SOH (%)", row=1, col=1)
                fig.update_yaxes(title_text="Voltage (V)", row=1, col=2)
                fig.update_layout(template="plotly_white", showlegend=True)
                result_chart = st.plotly_chart(fig, use_container_width=True)
                st.dataframe(rdf.set_index("days"), use_container_width=True)
            else:
                st.error(
                    "Simulation results file not found. Please run the simulation first."
                )


with tabs[1]:
    st.subheader("Postprocessing Tools")
    if not os.path.exists("./sim_data"):
        st.error("No data to process. Please run a simulation once")
    else:
        st.subheader("Plot configuration")
        summary_data = st.checkbox("Summary variables plot", value=True)
        voltage_components = st.checkbox("Voltage components plot")

        pp = PostProcessor()
        if summary_data:
            st.plotly_chart(pp.plot_summary_variables())
        if voltage_components:
            start_day = st.number_input("Start day", min_value=1, value=1, step=1)
            end_day = st.number_input(
                "End day",
                min_value=start_day + 1,
                value=2,
                step=1,
                max_value=len(os.listdir("sim_data") - 1),
            )
            split_by_electrode = st.checkbox("Split by Electrodes")
            st.write(f"Plotting data from day {start_day} to day {end_day}")
            st.plotly_chart(
                pp.plot_voltage_components(
                    days=range(start_day - 1, end_day),
                    split_by_electrode=split_by_electrode,
                )
            )
    if st.button("View summary data"):
        st.dataframe(pd.read_csv("./sim_data/simulation summary data.csv"))
    if st.button("View daywise data"):
        daywise_df = pd.concat(
            [
                pd.read_parquet(f"./sim_data/day_{day+1}_full_data.parquet")
                for day in range(start_day - 1, end_day)
            ]
        )
        st.dataframe(daywise_df)
