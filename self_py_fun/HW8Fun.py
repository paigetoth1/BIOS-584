import os
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as bpdf

# Methods for trunc_mean_cov, plotting trunc_mean, and plotting trunc_mean_cov

def produce_trunc_mean_cov(input_signal, input_type, E_val):
    type_mask = (input_type == 1)

    input_signal_target = input_signal[type_mask]
    input_signal_not_target = input_signal[~type_mask]

    signal_tar_mean = []
    signal_ntar_mean = []
    signal_tar_cov = []
    signal_ntar_cov = []
    signal_all_cov = []

    length_per_electrode = int(len(input_signal[0]) / E_val)

    prev_idx = 0
    idx = length_per_electrode

    for electrode in range(E_val):
        signal_tar_mean.append(np.mean(input_signal_target[prev_idx:idx], axis=1))
        signal_ntar_mean.append(np.mean(input_signal_not_target[prev_idx:idx], axis=1))
        signal_tar_cov.append(np.cov(input_signal_target[prev_idx:idx]))
        signal_ntar_cov.append(np.cov(input_signal_not_target[prev_idx:idx]))
        signal_all_cov.append(np.cov(input_signal[prev_idx:idx]))
        prev_idx += length_per_electrode
        idx += length_per_electrode

    return [signal_tar_mean, signal_ntar_mean, signal_tar_cov, signal_ntar_cov, signal_all_cov]


def plot_trunc_mean(eeg_tar_mean, eeg_ntar_mean, subject_name, time_index, E_val, electrode_name_ls, y_limit=np.array([-5, 8]), fig_size=(12, 12)):

    fig, axes = plt.subplots(4, 4, figsize=fig_size)
    fig.suptitle(str(subject_name), fontsize=16, y=0.98)

    for electrode in range(E_val):
        row = electrode // 4
        col = electrode % 4
        ax = axes[row, col]
        ax.plot(time_index, eeg_tar_mean[electrode], color='red', label='Target')
        ax.plot(time_index, eeg_ntar_mean[electrode], color='blue', label='Non-Target')
        ax.set_title(electrode_name_ls[electrode])
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Amplitude (muV)")
        if y_limit is not None:
            ax.set_ylim(y_limit)
        ax.legend(fontsize='small')
        ax.grid(True, linestyle='-', linewidth=0.4, alpha=0.6)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save plot as "Mean.png"
    output_directory = r"K114"
    filename = "Mean.png"
    full_path = os.path.join("..", output_directory, filename)
    plt.savefig(full_path)
    plt.close()

def plot_trunc_cov(eeg_cov, cov_type, time_index, subject_name, E_val, electrode_name_ls, fig_size=(14,12)):

    X, Y = np.meshgrid(time_index, time_index)

    max_abs = np.max(np.abs(eeg_cov))
    vmin, vmax = -max_abs, max_abs

    fig, axes = plt.subplots(4, 4, figsize=fig_size)
    fig.suptitle(f"{subject_name} — {cov_type}", fontsize=16, y=0.96)

    last_cf = None
    for electrode in range(E_val):
        row = electrode // 4
        col = electrode % 4
        ax = axes[row, col]

        cov = eeg_cov[electrode]
        cf = ax.contourf(X, Y, cov, levels=50, cmap='seismic', vmin=vmin, vmax=vmax)
        last_cf = cf

        ax.invert_yaxis()
        ax.set_title(electrode_name_ls[electrode])
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Time (ms)")
        ax.tick_params(axis='both', which='major', labelsize=8)

    fig.subplots_adjust(right=0.88, top=0.94, left=0.06, bottom=0.06, hspace=0.4, wspace=0.4)
    cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
    fig.colorbar(last_cf, cax=cbar_ax, label='Covariance')

    #Use the cov_type string parameter when determining the output file name
    #Use "Covariance_" as the first part of the string, and concatenate that with cov_type to get
    #"Covariance_Target", "Covariance_Non-Target", and "Covariance_All"

    output_directory = r"K114"
    filename = "Covariance_" + cov_type + ".png"

    full_path = os.path.join("..", output_directory, filename)
    plt.savefig(full_path)
    plt.close()