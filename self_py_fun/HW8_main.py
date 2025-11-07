import os
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as bpdf
import HW8Fun

#Global Variables
bp_low = 0.5
bp_upp = 6
electrode_num = 16
electrode_name_ls = ['F3', 'Fz', 'F4', 'T7', 'C3', 'Cz', 'C4', 'T8', 'CP3', 'CP4', 'P3', 'Pz', 'P4', 'PO7', 'PO8', 'Oz']
parent_dir = 'C:/Users/paige/OneDrive/Documents/GitHub/BIOS-584'
parent_data_dir = '{}/data'.format(parent_dir)
time_index = np.linspace(0, 800, 25)

subject_name = 'K114'
session_name = '001_BCI_TRN'

#Create Directory if it does not exist
if not os.path.exists('C:/Users/paige/OneDrive/Documents/GitHub/BIOS-584/subject_name'):
    os.mkdir('C:/Users/paige/OneDrive/Documents/GitHub/BIOS-584/subject_name')
    print("Directory created")
else:
    print("Directory already exists")

# Load in the MATLAB Data:
eeg_trunc_obj = sio.loadmat('C:/Users/paige/OneDrive/Documents/GitHub/BIOS-584/data/K114_001_BCI_TRN_Truncated_Data_0.5_6.mat')

# Extract data from the dictionary
eeg_trunc_signal = eeg_trunc_obj['Signal']
eeg_trunc_type = eeg_trunc_obj['Type']

# Squeeze the dataframe
eeg_trunc_type = np.squeeze(eeg_trunc_type, axis=1)

# Call methods
output = HW8Fun.produce_trunc_mean_cov(eeg_trunc_signal, eeg_trunc_type, 16)
HW8Fun.plot_trunc_mean( output[0], output[1], subject_name, time_index, 16, electrode_name_ls, y_limit=np.array([-5, 8]), fig_size=(12, 12))

HW8Fun.plot_trunc_cov(output[2], "Target", time_index, subject_name, 16, electrode_name_ls, fig_size=(14,12))
HW8Fun.plot_trunc_cov(output[3], "Non-Target", time_index, subject_name, 16, electrode_name_ls, fig_size=(14,12))
HW8Fun.plot_trunc_cov(output[4], "All", time_index, subject_name, 16, electrode_name_ls, fig_size=(14,12))