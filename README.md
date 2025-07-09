# olabatsim_gui

A Streamlit-based graphical user interface for running, visualizing, and analyzing battery cell simulations using PyBaMM and olabatsim.

## About The Project

This application provides an interactive platform for researchers and engineers to simulate the performance and degradation of lithium-ion battery cells. It leverages the power of PyBaMM for the underlying electrochemical models and provides a user-friendly interface built with Streamlit to configure and analyze simulation results without needing to write code for every experiment.

### Key Features:

  * **Interactive Simulation Setup**: Easily configure your battery model, including options for the Single Particle Model with electrolyte (SPMe) or the Doyle-Fuller-Newman (DFN) model.
  * **Advanced Degradation Modeling**: Incorporate various degradation mechanisms such as Solid Electrolyte Interphase (SEI) formation, SEI-induced porosity changes, SEI on cracks, lithium plating, and loss of active material.
  * **Customizable Solver Settings**: Fine-tune the Casadi solver with options for mode, tolerances, and step controls for a balance between simulation speed and accuracy.
  * **Drive Cycle Simulation**: Upload your own drive cycle data from a CSV file to run realistic simulations.
  * **Data Feasibility Check**: Before running a full simulation, check the quality and feasibility of your uploaded drive cycle data.
  * **Parameter Editing**: Interactively edit SEI parameters, operating conditions, and thermal parameters directly within the GUI.
  * **Live Simulation Progress**: Monitor the simulation progress in real-time and have the ability to stop the simulation.
  * **Rich Visualization**: View simulation results, including State of Health (SOH) and voltage profiles, through interactive plots powered by Plotly.
  * **Post-Processing Tools**: Analyze simulation outputs with built-in tools to plot summary variables and detailed voltage components for specific day ranges.
  * **Data Export**: View and access both summary and detailed day-wise simulation data.

## Getting Started

Follow these instructions to set up and run the Cell Simulation GUI on your local machine.

### Prerequisites

You need to have Python installed on your system. This project and its dependencies can be installed using `pip`.

### Installation

1.  **Clone the repository (if applicable) or save the Python script.**

2.  **Install the required Python libraries:**

    ```bash
    pip install git+https://github.com/harisankarsuresh/olabatsim_gui.git
    ```

## Usage

1.  **Call the gui from terminal or cmd**
    Open your terminal, Run this command to start the project:

    ```bash
    olabatsim-gui
    ```

2.  **Configure the Simulation:**
    Use the sidebar to set up your simulation:

      * **Model Selection**: Choose between the `SPMe` and `DFN` models.
      * **Degradation Mechanisms**: Select options for SEI, thermal effects, and other degradation phenomena.
      * **Solver Settings**: Adjust the Casadi solver parameters for optimal performance.
      * Click "**Apply Configuration**".

3.  **Upload Drive Cycle Data:**

      * In the "Simulation Plot" tab, use the file uploader to select and upload a CSV file containing your drive cycle data. The CSV should have columns for time and current/power.

4.  **Check Data Feasibility:**

      * Once the file is uploaded, you can click "**Plot Data Quality**" to inspect the uploaded data and ensure it's suitable for simulation.

5.  **Adjust Parameters (Optional):**

      * Use the checkboxes to display and edit **SEI parameters**, **Operating Conditions**, and **Thermal Parameters**.
      * Click "**Apply Settings**" to save your changes.

6.  **Run the Simulation:**

      * Enter the number of days you want to simulate.
      * Click the "**Run Simulation**" button to start. You can monitor the progress and stop the simulation at any time using the "**Stop Simulation**" button.

7.  **Visualize and Analyze Results:**

      * After the simulation is complete, click "**Plot results**" to see the SOH and voltage plots.
      * Navigate to the "**Postprocessing**" tab to use more advanced analysis tools, such as plotting summary variables or detailed voltage components. You can also view the raw summary or day-wise data in dataframes.

-----
