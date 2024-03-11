import matplotlib.pyplot as plt
import numpy as np

# x_values = np.linspace(0, 100, 10000)


def plot_waveform(
    x_values, y_values, title="Waveform", x_label="Time", y_label="Amplitude"
):
    """
    Plots a waveform given x and y values.

    Parameters:
    - x_values: Array-like, the x values for the plot.
    - y_values: Array-like, the y values for the plot.
    - title: str, the title of the plot.
    - x_label: str, the label for the x-axis.
    - y_label: str, the label for the y-axis.
    """
    plt.figure(figsize=(10, 6))  # Optional: Specifies the figure size
    plt.plot(x_values, y_values, label="Waveform")  # Plot the waveform
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)  # Show grid lines for better readability
    plt.legend()  # Show legend
    plt.show()
