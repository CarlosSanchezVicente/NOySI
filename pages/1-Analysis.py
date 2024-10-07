# IMPORTS LIBRARIES
import pandas as pd
import duckdb
import streamlit as st 
import altair as alt
import datetime
import re

# AUTHENTICATION STATUS
st.logo('./img/NoySI.png', size="medium")
if not st.session_state['authentication_status']:
    st.info('Please Login from the Home page and try again.')
    st.stop()

# Necessary to use duckdb module in streamlit
#atp_duck = duckdb.connect('atp.duck.db', read_only=True)

# DEFINE
#line_req = ''
sensor_req = ''
gas_req = ''
start_time_req = None
end_time_req = datetime.datetime.now()
#¡¡¡¡¡¡¡ ATENTION:Change the sensors_hist by sensor_current!!!!!!
query_basic = """
SELECT
    mea.ID,
    mea.conn_measurement,
    mea.id_measurement,
    mea.record_created_time,
    mea.project,
    mea.gases_line_used,
    sen.name_sensor,
    sen.solutions_used,
    gas.name_gas
FROM measurements_hist AS mea
JOIN sensors_hist AS sen ON mea.id_sensor = sen.id_sensor
JOIN gases_hist AS gas ON mea.id_gases = gas.id_gas;
"""
query_electrical = """
SELECT
    ID,
    file_title,
    time_s,
    sensor1_ohm,
    sensor2_ohm,
    sensor3_ohm,
    sensor4_ohm,
    bottle1_ppb,
    bottle2_ppb,
    bottle3_ppb,
    date_timestamp
FROM data_methane_line
WHERE file_title = ?;
 """
query_solutions = """
SELECT 
    sol.name_solution,
    mat.name_material
FROM solutions_hist AS sol
JOIN materials_hist AS mat ON sol.id_solute = mat.id_material
WHERE id_solution = ?
"""
query_drift= """
SELECT 
    file_title,
    time_s,
    bottle1_ppb,
    bottle2_ppb,
    bottle3_ppb,
    s1_without_drift,
    s2_without_drift,
    s3_without_drift,
    s4_without_drift
FROM data_methane_processed
WHERE file_title = ?;
"""
query_response = """
SELECT 
    file_title,
    concentration_ppb,
    s1_without_drift,
    s2_without_drift,
    s3_without_drift,
    s4_without_drift
FROM data_methane_response
WHERE file_title = ?;
"""
query_optical = """
SELECT 
    experiment_name,
    current_timestamp,
    axis,
    spectra
FROM optical_spectra
WHERE experiment_name = ?;
"""
query_pos = """
SELECT
    file_title,
    bottle_cycle_ppb,
    final_date_timestamp
FROM data_methane_pos
WHERE file_title = ?;
 """

# CONFIGURATION PAGE
#st.title('Data analysis and plot the experiment')
st.set_page_config(
        page_title='Analysis',
        page_icon='📈'
    )
#st.sidebar.success('Select the parameters:')
st.sidebar.markdown("### Select the parameters:")



# AUXILIARY FUNCTIONS
def filter_df(df, column_result, column_filter, var_req, start_time_req, end_time_req):

    # Filter u
    if (var_req != '') and (start_time_req == None):
        df_filtered = df[df[column_filter] == var_req]
        print(df_filtered)
        print('Entra en 1')

    # Filter only by start_time_req
    elif (start_time_req != None) and (var_req == ''):
        df_filtered = df[(df['record_created_time'] >= start_time_req) & 
                         (df['record_created_time'] <= end_time_req)]
        print('Entra en 2')
    
    # Filter using both
    elif (start_time_req != None) and (var_req == ''):
        df_filtered = df[(df['record_created_time'] >= start_time_req) & 
                         (df['record_created_time'] <= end_time_req) & 
                         (df[column_filter] == var_req)]
        print('Entra en 3')

    # No filter
    else:
        df_filtered = df
        print('Entra en 4')

    list = df_filtered[column_result].unique()
    names = ['']
    names.extend(list)

    return names, df_filtered


def get_nonzero_column(df):
    temp_df = df.filter(like='bottle')
    nonzero_counts = temp_df.sum()  # Contar valores no cero por columna
    nonzero_column = nonzero_counts[nonzero_counts != 0].idxmax()
    return nonzero_column


@st.cache_data   # With this line, it's possible to store in cache this function, and it will only be executed if 'new_configurante' changes
def update_last_configuration(new_configuration):
    last_configuration = new_configuration
    return last_configuration


@st.cache_data
def extract_sensor_materials(string_solutions):
    # Split the string
    solutions_list = string_solutions.split(', ')

    # Create empty dataframe
    solutions_df = pd.DataFrame()

    # Extract the material data from the database
    for element in solutions_list:
        # Estract the solution for each id
        solutions_new_df = con.execute(query_solutions, ([element,])).df()
        
        # Append the data to the dataframe
        if solutions_df.empty:
            solutions_df = solutions_new_df.copy()
        else:
            solutions_df = pd.concat([solutions_df, solutions_new_df], ignore_index=True)

    # Rename the index
    sensors_name = ['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4']
    solutions_df['Sensor names'] = sensors_name
    solutions_df.set_index('Sensor names', inplace=True)

    # Rename the column names
    new_names = {'name_solution': 'Solution used',
                'name_material': 'Material used'}
    solutions_df = solutions_df.rename(columns=new_names)
    return solutions_df


def checkbox_container():
    cols = st.columns(4)
    if cols[0].button('Raw data', type='secondary'):
        type_process = 'raw_data'
    if cols[1].button('Filtered data', type='secondary'):
        type_process = 'filtered_data'
    if cols[2].button('Drift-corrected data', type='secondary'):
        type_process = 'drift_data'
    if 'type_process' not in locals():
        type_process = ''

    return type_process


def obtain_optical_spectra(data_optical_df, data_pos_df):
    # Remove the last semicycle in the data_pos_df if the concentration is zero
    if data_pos_df.iloc[-1]['bottle_cycle_ppb'] == 0:
        data_pos_df = data_pos_df.iloc[:-1]

    # Transform date column from string to datetime
    data_optical_df['current_timestamp'] = pd.to_datetime(data_optical_df['current_timestamp'])
    data_pos_df['final_date_timestamp'] = pd.to_datetime(data_pos_df['final_date_timestamp'])

    # Inicializate the dataframe to store data
    results = []

    # Iterate over the hour in data_pos_df
    for index, row in data_pos_df.iterrows():
        hour = row['final_date_timestamp']
        # Find the last spectra for each cycle
        last_spectra = data_optical_df[data_optical_df['current_timestamp'] < hour].iloc[-1]
        # Store data in results dataframe 
        results.append([row['file_title'], last_spectra['current_timestamp'], last_spectra['axis'], last_spectra['spectra']])

    # Create the dataframe
    result_df = pd.DataFrame(results, columns=['file_title', 'current_timestamp', 'axis', 'spectra'])
    
    return result_df


def convert_str_to_numbers(string_lista):    
    # Patrón de expresión regular para encontrar números
    patron_numeros = r'\d+\.\d+'

    # Buscar todos los números en el string usando el patrón
    numeros = re.findall(patron_numeros, string_lista)

    # Convertir los números de cadena a punto flotante
    numeros = [float(num) for num in numeros]
    spectra_df = pd.DataFrame(numeros)
    
    return spectra_df


def obtain_correct_spectra(data_pos_df, intensities_df):
    columns_names =  list(data_pos_df['bottle_cycle_ppb'])

    spectra_complete_df = pd.DataFrame()

    for i in range(len(intensities_df)):
        string_lista = intensities_df['spectra'][i]
        
        # Convert the list with string to list with numbers
        spectra_df = convert_str_to_numbers(string_lista)
        
        # Rename the column name
        column_name = f"Cycle {i+1} ({columns_names[i]} ppb)"
        spectra_df.columns = [column_name]
        print(spectra_df)
            
        if spectra_complete_df.empty:
            spectra_complete_df = spectra_df.copy()
        else:
            spectra_complete_df = pd.concat([spectra_complete_df, spectra_df], axis=1)
            
    return spectra_complete_df


def select_concentration_to_plot(df, concentration, wavelength_numbers_df):
    # Obtain which is the column with this concentration value
    selected_column = None
    for column in df.columns:
        if str(concentration) in column:
            selected_column = column
            break
            
    # Obtain the column selected index
    column_index = df.columns.get_loc(selected_column)
    # Obtain the previous column
    previous_column = df.columns[column_index - 1]
    # Create new dataframe with previous and selected columns
    new_df = df[[previous_column, selected_column]]
    # Rename the column of wavelength_numbers_df
    wavelength_numbers_df.columns = ['Wavelength (nm)']
    # Concat the dataframe with wavelength column
    new_df = pd.concat([wavelength_numbers_df, new_df], axis=1)

    return new_df


# CONNECTION TO DATABASE
# Create a connection to a file called 'LabSilver.db'
con = duckdb.connect("./data/Silver/LabSilver.db")
# Create a connection to a file called 'gold_lab.db'
conn = duckdb.connect("./data/Gold/LabGold.db")
# Basic Query 
data_experiment_df = con.execute(query_basic).df()


# ANALYSIS PAGE
# SIDEBAR CONFIGURATION
# Selectbox: select the line used
line_req = st.sidebar.selectbox('Select the line used: *', ['MethaneLine', 'OzoneLine', 'PermeationLine'])


# Obtain the gases names
# Obtain the gases names filtered
gases_name, df_filtered = filter_df(data_experiment_df, 'name_gas', 'name_sensor',sensor_req, start_time_req, end_time_req)
# Selectbox: select the measured gas
gas_req = st.sidebar.selectbox('Select the measured gas: *', gases_name)


# Obtain the sensors names filtered
sensor_name, df_filtered = filter_df(data_experiment_df, 'name_sensor', 'name_gas', gas_req, start_time_req, end_time_req)
# Selectbox: select the sensor name
sensor_req = st.sidebar.selectbox('Select the multisensor used:', options=sensor_name)


# Date_imput: select the time range
start_time_req = st.sidebar.date_input('Select the start date range:', value=None, format="YYYY/MM/DD")
end_time_req = st.sidebar.date_input('Select the end date range:')
# If end_date is previous than start_date
if start_time_req != None:
    if end_time_req < start_time_req:
        st.error('The min_time variable must be a date earlier than the one stored in max_time.', icon='🚨')



# Filter the name
if sensor_req == '':
    exp_names = df_filtered['conn_measurement']
else:
    # Filter the dataframe
    df_filtered = df_filtered[df_filtered['name_sensor'] == sensor_req]
    # Obtain the experiments names of record filtered
    exp_names = df_filtered['conn_measurement']
# Selectbox: select the experiment name
exp_names_sorted = sorted(exp_names, key=lambda x: int(x.split("-")[1]), reverse=True)   # Sort the names
exp_name_req = st.sidebar.selectbox('Select the experiment name: *', exp_names_sorted)


# PAGE CONFIGURATION
# Update configuration page on streamlit
new_configuration = [line_req, gas_req, sensor_req, start_time_req, end_time_req, exp_name_req]
last_configuration = update_last_configuration(new_configuration)


# PLOT
# The button will not appear if all the required fields have not been filled in.
if (line_req != '') and (gas_req != '') and (exp_name_req != ''):
    # Button: plot the graph
    if st.sidebar.button('Plot', type='primary') or last_configuration == new_configuration:
        # TITLE: Datetime_range: select the time range
        st.markdown("## Data analysis and plotting")

        # Extract data from database (silver)
        data_electrical_df = con.execute(query_electrical, ([exp_name_req,])).df()
        # Extract data from database (gold)
        data_drift_df = conn.execute(query_drift, ([exp_name_req,])).df()
        
        # TABLE: Plot the table with sensor caracteristics
        solutions_used_value = data_experiment_df.loc[data_experiment_df['conn_measurement'] == exp_name_req, 'solutions_used'].values[0]
        sensor_materials_df = extract_sensor_materials(solutions_used_value)
        st.markdown('#### Sensor matrix composition')
        st.table(sensor_materials_df)
        st.markdown("""---""")

        # PLOT ELECTRICAL DATA
        st.markdown("### Electrical data")

        # Checkbox to select plot configuration
        checkbox_names = ['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4']
        sensor_select = st.radio('Plot configuration', checkbox_names, horizontal=True)
        #st.markdown('##')   # Add blanck space between two streamlit components
        type_process = checkbox_container()
        st.markdown('##')   # Add blanck space between two streamlit components
        st.markdown('##### Dynamic response ($\Omega$)')

        # Plot the graph
        # Obtain the concentration column: apply the lambda function to the columns: bottle1_ppb, bottle2_ppb, bottle3_ppb
        nonzero_column = get_nonzero_column(data_electrical_df)

        # Plot graph with double y-axis
        #st.markdown('#### Sensor graph')
        if sensor_select == 'Sensor 1':
            if type_process == 'raw_data' or type_process == '':
                a = alt.Chart(data_electrical_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('sensor1_ohm', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")
            elif type_process == 'drift_data':
                a = alt.Chart(data_drift_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('s1_without_drift', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")

        elif sensor_select == 'Sensor 2':
            if type_process == 'raw_data' or type_process == '':
                a = alt.Chart(data_electrical_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('sensor2_ohm', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")
            elif type_process == 'drift_data':
                a = alt.Chart(data_drift_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('s2_without_drift', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")

        elif sensor_select == 'Sensor 3':
            if type_process == 'raw_data' or type_process == '':
                a = alt.Chart(data_electrical_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('sensor3_ohm', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")
            elif type_process == 'drift_data':
                a = alt.Chart(data_drift_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('s3_without_drift', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")

        elif sensor_select == 'Sensor 4':
            if type_process == 'raw_data' or type_process == '':
                a = alt.Chart(data_electrical_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('sensor4_ohm', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")
            elif type_process == 'drift_data':
                a = alt.Chart(data_drift_df).mark_line(stroke='#5276A7', interpolate='monotone').encode(
                    alt.X('time_s', title='Time (s)'),
                    alt.Y('s4_without_drift', title='Sensor resistance (Ohm)', axis=alt.Axis(tickCount=10, format=".1e")),
                    color=alt.Color('response_label:N').scale(range=['#5276A7']).title('Legend')
                ).transform_calculate(response_label="'Sensor response'")

        b = alt.Chart(data_electrical_df).mark_line(stroke='#57A44C', interpolate='monotone').encode(
            alt.X('time_s', title='Time (s)'),
            alt.Y(nonzero_column, title='Gas concentration (ppb)', axis=alt.Axis(tickCount=10)),   #, format=".1e"
            color=alt.Color('concentration_label:N').scale(range=['#57A44C']).title(None)
        ).transform_calculate(concentration_label="'Gas concentration'")

        scale_kwargs = dict(domain=['response_label:N', 'concentration_label:N'], range=["#5276A7", "#57A44C"])

        c = alt.layer(a, b).resolve_scale(
            y='independent',
            color='independent',
        ).properties(
            width=750,  # Ajustar el ancho del gráfico según sea necesario
            height=350
        )

        st.altair_chart(c, theme="streamlit")

        # PLOT RESPONSE DATA
        # Extract data from database (gold)
        st.markdown('##')   # Add blanck space between two streamlit components
        st.markdown('##### Response (%)')
        data_response_df = conn.execute(query_response, ([exp_name_req,])).df()
        
        # Change the columns names
        new_names = {'concentration_ppb': 'Concentration (ppb)', 's1_without_drift': 'S1 response', 's2_without_drift': 'S2 response', 's3_without_drift': 'S3 response', 's4_without_drift': 'S4 response'}
        data_response_df_trans = data_response_df.rename(columns=new_names)

        # Transform the data to plot
        melted_df = pd.melt(data_response_df_trans, 
                            id_vars=['Concentration (ppb)'],
                            value_vars=['S1 response', 'S2 response', 'S3 response', 'S4 response'], 
                            var_name='Legend', 
                            value_name='Response (%)')
        
        # Plot the graph
        d = alt.Chart(melted_df).mark_line(
            point=True
        ).encode(
            x='Concentration (ppb)',
            y='Response (%)',
            color='Legend'
        ).properties(
            width=750,  # Ajustar el ancho del gráfico según sea necesario
            height=350
        )
        st.altair_chart(d)

        # PLOT OPTICAL DATA
        #st.table(data_electrical_df)
        st.markdown("""---""")
        

        # Plot electrical data
        st.markdown("### Optical data")
        # Obtain the optical data from database
        data_optical_df = con.execute(query_optical, ([exp_name_req,])).df()
        data_pos_df = conn.execute(query_pos, ([exp_name_req,])).df()
        concentrations = tuple(data_pos_df[data_pos_df['bottle_cycle_ppb'] != 0]['bottle_cycle_ppb'].astype(str))

        # Transform the wavelength dataframe
        wavelength_numbers_df = convert_str_to_numbers(data_optical_df['spectra'][0])

        # Transfrom the intensities dataframe
        intensities_string_df = obtain_optical_spectra(data_optical_df, data_pos_df)
        spectra_numbers_df = obtain_correct_spectra(data_pos_df, intensities_string_df)

        # Plot the selectrbox
        option = st.selectbox(
            'Which optical spectrum do you want to see?', 
            concentrations,
            index=None,
            placeholder='Select the concentration of the cycle you want to view')
        
        # Transform the optical data to plot
        if option != None:
            # Obtain the data to plot
            option_int = int(option)
            spectra_selected_df = select_concentration_to_plot(spectra_numbers_df, option_int, wavelength_numbers_df)
            names_to_plot = spectra_selected_df.columns[1:].tolist()

            # Plot config
            opt_df = pd.melt(spectra_selected_df, 
                             id_vars=['Wavelength (nm)'],
                             value_vars=names_to_plot, 
                             var_name='Legend', 
                             value_name='Intensity')
                             
        
            # Plot the optical graph
            e = alt.Chart(opt_df).mark_line(
                strokeWidth=0.5
            ).encode(
                x='Wavelength (nm)',
                y='Intensity',
                color='Legend'
            ).properties(
                width=750,  # Ajustar el ancho del gráfico según sea necesario
                height=350
            )
            st.altair_chart(e)
        