import os
import scipy.io as sio
from self_py_fun.DebugFun import *

bp_low = 0.5
bp_upp = 6
electrode_num = 16
parent_dir = '/Users/tma33/Library/CloudStorage/OneDrive-EmoryUniversity/Emory/Rollins SPH/2025/BIOS-584/python_proj'
parent_data_dir = '{}/data'.format(parent_dir)
time_index = np.linspace(0, 800, 25)
electrode_name_ls = ['F3', 'Fz', 'F4', 'T7', 'C3', 'Cz', 'C4', 'T8', 'CP3', 'CP4', 'P3', 'Pz', 'P4', 'PO7', 'PO8', 'Oz']

subject_name = 'K114'
# create a new folder called K114
subject_dir = '{}/{}'.format(parent_dir, subject_name)
if not os.path.exists(subject_dir):
    os.mkdir(subject_dir)
session_name = '001_BCI_TRN'
complete_trunc_data_name = '{}_{}_Truncated_Data_{}_{}'.format(subject_name, session_name, bp_low, bp_upp)
complete_trunc_data_dir = '{}/{}.mat'.format(parent_data_dir, complete_trunc_data_name)
eeg_trunc_obj = sio.loadmat(complete_trunc_data_dir)

print(eeg_trunc_obj.keys())
eeg_trunc_signal = eeg_trunc_obj['Signal']
print(eeg_trunc_signal.shape) # 3420, 400
eeg_trunc_type = eeg_trunc_obj['Type']
print(eeg_trunc_type.shape) # 3420, 1
eeg_trunc_type = np.squeeze(eeg_trunc_type, axis=1)

[eeg_trunc_tar_mean, eeg_trunc_ntar_mean,
 eeg_trunc_tar_cov, eeg_trunc_ntar_cov,
 eeg_trunc_all_cov] = produce_trun_mean_cov(eeg_trunc_signal, eeg_trunc_type, electrode_num)

plot_trunc_mean(eeg_trunc_tar_mean, eeg_trunc_ntar_mean, subject_name, time_index, electrode_num, electrode_name_ls,
                y_limit=np.array([-5, 8]))