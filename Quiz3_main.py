
def compute_D_partial_for_task_1_only(input_signal):
    r"""
    :param input_signal:
    """
    T_len = len(input_signal)
    signal_diff_one = input_signal[-1] - input_signal[1:] # i think this is the first issue,
    # because it would only calculates the difference between a slice of all the elements except the last one
    and the last element of the sequence input_signal[-1]
    D_val = np.sum(np.sqrt(1+signal_diff_one**2)) / (T_len - 1)
    return D_val


# You can use this .py script to perform debugging task.
sample_arr_1 = np.array([1,2,3,4,5])
d_1 = compute_D_partial(sample_arr_1) #this is where I believe the issue is.
# I think this code computes the square root of 1+2+3+4+5 (which is 15
print(d_1)
# The correct d_1 should be 5.66.
