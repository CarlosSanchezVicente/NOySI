# IMPORTS
from nptdms import TdmsFile   # Import tdms files


# AUXILIARY FUNCTIONS



# MAIN FUNCTIONS
def read_tdms_file():

    for 
        # Read the TDMS file
            tdms_file = TdmsFile.read(complete_path)

            # Create a DataFrame with the data from the TDMS file. Here you must adjust how to extract and organize your data according 
            # to the structure of your file. In this example, it is assumed that the data are in specific groups and channels.
            data = {}
            for group in tdms_file.groups():
                for channel in group.channels():
                    data[channel.name] = channel[:].tolist()
        
            # Transform data list to dataframe
            exec(f"{name_dataframe} = pd.DataFrame(data)")
            #print(name_dataframe)