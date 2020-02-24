import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import plotly
import plotly.graph_objects as go
import plotly.figure_factory as ff
import seaborn as sns
import pandas as pd
import numpy as np
import glob
import re
import os
from pathlib import Path
from pdb import set_trace
import scipy.stats as stats


def find_intersection_of_gaussians(m1, m2, std1, std2):
    a = 1 / (2 * std1 ** 2) - 1 / (2 * std2 ** 2)
    b = m2 / (std2 ** 2) - m1 / (std1 ** 2)
    c = m1 ** 2 / (2 * std1 ** 2) - m2 ** 2 / (2 * std2 ** 2) - np.log(std2 / std1)
    return np.roots([a, b, c])


def plot_gaussian(mu=0, std=1, x=None,
                  y_label=None, x_label=None, title=None,
                  filename="./results/plot_2_gaussian_output.png", showfig=False, savefig=True):
    """
    Plot a gaussian function
    :param mu: mean of the gaussian
    :param std:  Standard deviation of the gaussian
    :param x: The x axis linespace data. If None, an automatic one will be generated. Default is None
    :param y_label: The y axis label.
    :param x_label: The x axis label.
    :param title: str or None. The legend’s title. Default is no title (None).
    :param filename: Only used when savefig=True. The name of the figure to be saved
    :param showfig: Boolean. If true it will show the figure using matplotlib show method
    :param savefig: Boolean. If true it will save the figure with the name of filename parameter
    :return: tuple (fig, ax) from the plotted figure
    """
    if x is None:
        x = np.linspace(mu - 3 * std, mu + 3 * std, 100)
    fig, ax = plt.subplots()
    ax.plot(x, stats.norm.pdf(x, mu, std))

    # Figure parameters
    if y_label is not None:
        ax.set_ylabel(y_label)
    if x_label is not None:
        ax.set_xlabel(x_label)
    if title is not None:
        fig.suptitle(title)

    # save/show results
    if savefig:
        fig.savefig(filename)
    if showfig:
        fig.show()
    return fig, ax


def plot_2_gaussian(mu_1, std_1, mu_2, std_2, name_1, name_2, x=None, y_label=None, x_label=None, loc=None, title=None,
                    filename="./results/plot_2_gaussian_output.png", showfig=False, savefig=True):
    """
    Plots 2 gaussians on the same plot using matplotlib
    :param mu_1: Mean of first gaussian to be plotted
    :param std_1: Standard deviation of the first gaussian to be plotted
    :param mu_2: Mean of second gaussian to be plotted
    :param std_2: Standard deviation of the second gaussian to be plotted
    :param name_1: Name of the first gaussian (Used in legend)
    :param name_2: Name of the second gaussian (Used in legend)
    :param x: The x axis linespace data. If None, an automatic one will be generated. Default is None
    :param y_label: The y axis label.
    :param x_label: The x axis label.
    :param loc: can be a string or an integer specifying the legend location. default: None.
                    https://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend
    :param title: str or None. The legend’s title. Default is no title (None).
    :param filename: Only used when savefig=True. The name of the figure to be saved
    :param showfig: Boolean. If true it will show the figure using matplotlib show method
    :param savefig: Boolean. If true it will save the figure with the name of filename parameter
    :return: tuple (fig, ax) from the plotted figure
    """
    # Get x axes
    ax_min = min(mu_1 - 3 * std_1, mu_2 - 3 * std_2)
    ax_max = max(mu_1 + 3 * std_1, mu_2 + 3 * std_2)

    # Get gaussian data
    if x is None:
        x, dx = np.linspace(ax_min, ax_max, 100, retstep=True)
    gauss_1 = stats.norm.pdf(x, mu_1, std_1)
    gauss_2 = stats.norm.pdf(x, mu_2, std_2)

    # plot gaussians
    fig, ax = plt.subplots()
    ax.plot(x, gauss_1, label=name_1)
    ax.plot(x, gauss_2, label=name_2)

    # plot intersection point
    result = find_intersection_of_gaussians(mu_1, mu_2, std_1, std_2)
    keep_root = [r for r in result if ax_max > r > ax_min]
    for k in keep_root:
        intersection_point = stats.norm.pdf(k, mu_1, std_1)
        ax.plot(k, intersection_point, 'o')
        ax.hlines(intersection_point, xmin=ax_min, xmax=k, linestyle='--', color='black')
        ax.vlines(k, ymin=0, ymax=intersection_point, linestyles='--', color='black')
        trans = transforms.blended_transform_factory(ax.get_yticklabels()[0].get_transform(), ax.transData)
        ax.text(0, intersection_point, "{:.2f}".format(intersection_point),
                transform=trans, ha="right", va="center")

    add_params(fig, ax, y_label, x_label, loc, title, filename, showfig, savefig)
    return fig, ax


def plot_2_hist_matplotlib(data_1, data_2, name_1, name_2, bins=None):
    """
    Plot 2 histograms in the same figure using matplotlib
    :param data_1: Data for the first histogram
    :param data_2: Data for the second histogram
    :param name_1: Name of the first histogram (Used in legend)
    :param name_2: Name of the second histogram (Used in legend)
    :param bins:  int or sequence or str, optional
    :return tuple (fig, ax) from the plotted figure
    """
    fig, ax = plt.subplots()
    if bins is None:
        bins = np.linspace(0, 1, 501)
    ax.hist(data_1, bins, alpha=0.5, label=name_1)
    ax.hist(data_2, bins, alpha=0.5, label=name_2)
    ax.axis(xmin=min(min(data_1), min(data_2)) - 0.01, xmax=max(max(data_1), max(data_2)) + 0.01)
    return fig, ax


def plot_hist_pandas(data, bins=None, column=None):
    fig = plt.figure()
    if bins is None:
        bins = data.shape[0] // 10
    ax = data.hist(column=column, bins=bins)
    return fig, ax


def plot_2_hist_seaborn(data_1, data_2, name_1, name_2, bins):
    fig = plt.figure()
    if bins is None:
        bins = np.linspace(0, 1, 501)
    ax = sns.distplot(data_1, bins, label=name_1)
    ax = sns.distplot(data_2, bins, label=name_2, ax=ax)
    ax.axis(xmin=min(min(data_1), min(data_2)) - 0.01, xmax=max(max(data_1), max(data_2)) + 0.01)
    return fig, ax


def add_params(fig, ax, y_label=None, x_label=None, loc=None, title=None,
               filename="./results/plot_2_gaussian_output.png", showfig=False, savefig=True):
    """
    :param fig:
    :param ax:
    :param y_label: The y axis label.
    :param x_label: The x axis label.
    :param loc: can be a string or an integer specifying the legend location. default: None.
                    https://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend
    :param title: str or None. The legend’s title. Default is no title (None).
    :param filename: Only used when savefig=True. The name of the figure to be saved
    :param showfig: Boolean. If true it will show the figure using matplotlib show method
    :param savefig: Boolean. If true it will save the figure with the name of filename parameter
    :return None:
    """
    # Figure parameters
    if loc is not None:
        fig.legend(loc=loc)
    if y_label is not None:
        ax.set_ylabel(y_label)
    if x_label is not None:
        ax.set_xlabel(x_label)
    if title is not None:
        fig.suptitle(title)
    # save/show results
    if showfig:
        fig.show()
    if savefig:
        fig.savefig(filename)


"""
Monte Carlo csv files
---------------------
saved on ./results/histogram_iter[0-9]+_classes[0-9]+.csv
"""


def plot_csv_histogram(filename, data1, data2, name_d1='CVNN', name_d2='RVNN', bins=None,
                       column=None, showfig=False, library='matplotlib'):
    """
    Plots and saves a histogram image using the data from a csv file with help of matplotlib.
    :param filename: Full path + name of the csv file to be opened (must contain the csv extension)
                TODO: automatically add the extension if it's not there
    :param bins: int or sequence or str, optional
    :param column:
    :param showfig: Boolean. If true it will show the figure using matplotlib show method
    :param library: TODO
    :return: None
    """
    assert type(filename) == str
    path, file = os.path.split(filename)
    if library == 'plotly':
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=np.array(data1), name=name_d1))
        fig.add_trace(go.Histogram(x=np.array(data2), name=name_d2))
        # Overlay both histograms
        fig.update_layout(barmode='overlay')
        # Reduce opacity to see both histograms
        fig.update_traces(opacity=0.75)
        plotly.offline.plot(fig, filename=path + '/' + library + "_histogram_" + file.replace(".csv", ".html"))
    elif library == 'matplotlib':
        fig, ax = plot_2_hist_matplotlib(np.array(data1), np.array(data2), name_d1, name_d2,
                                         bins=bins)
    elif library == 'pandas':
        # https://medium.com/python-pandemonium/data-visualization-in-python-histogram-in-matplotlib-dce38f49f89c
        fig, ax = plot_hist_pandas(data1, bins, column)     # TODO: this is not longer a pandas data CHECK THIS CASE!
    elif library == 'seaborn':
        fig, ax = plot_2_hist_seaborn(np.array(data1), np.array(data2), name_d1, name_d2, bins=bins)
    else:
        print("Warning: Unrecognized library to plot " + library)
        return None
    # Save the image with same name as csv
    if library is not 'plotly':
        add_params(fig, ax, x_label='Accuracy in %', title=library + ' histogram', loc='upper right',
                   showfig=showfig, savefig=False)
    fig.savefig(path + "/" + library + "_histogram_" + file.replace('.csv', '.png'))


def get_trailing_number(s):
    """
    Search for a termination of a file name that has the ".csv" extension and that has a number at the end.
    It gives the number at the end of the file. This number can have any amount of digits.
    Example:
    x = get_trailing_number("my/path/to/file/any_43_start_name9872.csv")    # x = 9872
    y = get_trailing_number("my/path/to/file/any_43_start_name.csv")        # y = None
    z = get_trailing_number("my/path/to/file/any_43_start_name85498.txt")   # y = None
    :param s: The string to search for the specific term
    :return: The number located before the extension. None if there is no number.
    """
    m = re.search(r'\d+.csv$', s)  # I get only the end of the string (last number of any size and .csv extension)
    # splitext gets root [0] and extension [1] of the name.
    return int(os.path.splitext(m.group())[0]) if m else None


def get_histogram_results(path="./"):
    """

    :param path:
    :return:
    """
    project_path = os.path.abspath(path)
    list_of_files = glob.glob(project_path + "/*[0-9].csv")  # csv files that will end with a number.
    d = dict()
    if list_of_files is not None:
        for file in list_of_files:
            k = get_trailing_number(file)
            val = get_loss_and_acc_means(file)
            if val is not None:
                if k in d:
                    d[k].append(val)
                else:
                    d[k] = [val]
    return d


def get_pandas_mean_for_each_class(d):
    result = dict()
    for k in d.keys():
        cvnn_loss = 0
        rvnn_loss = 0
        cvnn_acc = 0
        rvnn_acc = 0
        for dic in d[k]:
            cvnn_loss += dic['CVNN loss']
            rvnn_loss += dic['RVNN loss']
            cvnn_acc += dic['CVNN acc']
            rvnn_acc += dic['RVNN acc']
        result[k] = {'CVNN loss': cvnn_loss / len(d[k]),
                     'RVNN loss': rvnn_loss / len(d[k]),
                     'CVNN acc': cvnn_acc / len(d[k]),
                     'RVNN acc': rvnn_acc / len(d[k])}
    return pd.DataFrame(result).transpose()


def get_loss_and_acc_means(filename):
    try:
        data = pd.read_csv(filename)
        return data.mean().to_dict()
    except pd.errors.EmptyDataError:
        print("pandas.errors.EmptyDataError: get_loss_and_acc_means: No columns to parse from file")
        return None


def get_loss_and_acc_std(filename):
    try:
        data = pd.read_csv(filename)
        return data.std().to_dict()     # TODO: can return Nan with only one data
    except pd.errors.EmptyDataError:
        print("pandas.errors.EmptyDataError: get_loss_and_acc_means: No columns to parse from file")
        return None


"""
Loss and Acc saved csv
----------------------
saved on ./log/<name>/run-<date>/<name>.csv
"""


def plot_loss(filename, savefig=True, showfig=True, library='plotly'):
    assert type(filename) == str
    path, file = os.path.split(filename)
    data = pd.read_csv(filename)
    if library == 'matplotlib':
        fig, ax = plt.subplots()
        ax.plot(range(len(data["train loss"])),
                data["train loss"],
                'o-',
                label='train loss')
        ax.plot(range(len(data["test loss"])),
                data["test loss"],
                '^-',
                label='test loss')
        fig.legend(loc="upper right")
        ax.set_ylabel("epochs")
        ax.set_xlabel("loss")
        fig.suptitle("Train vs Test loss")
        if showfig:
            fig.show()
        if savefig:
            fig.savefig(path + "/" + library + "_loss_" + file.replace(".csv", ".png"))
    elif library == 'plotly':
        fig = go.Figure()
        color_train = 'rgb(255, 0, 0)'
        color_test = 'rgb(0, 255, 0)'
        assert len(data["train loss"]) == len(data["test loss"])
        x = list(range(len(data["train loss"])))
        fig.add_trace(go.Scatter(x=x,
                                 y=data["train loss"],
                                 mode='lines',
                                 name='train loss',
                                 line_color='rgb(255, 0, 0)'))
        fig.add_trace(go.Scatter(x=x,
                                 y=data["test loss"],
                                 mode='lines',
                                 name='test loss',
                                 line_color='rgb(0, 255, 0)'))

        # Add points
        fig.add_trace(go.Scatter(x=[x[-1]],
                                 y=[data["train loss"].to_list()[-1]],
                                 mode='markers',
                                 name='last value train',
                                 marker_color=color_train))
        fig.add_trace(go.Scatter(x=[x[-1]],
                                 y=[data["test loss"].to_list()[-1]],
                                 mode='markers',
                                 name='last value test',
                                 marker_color=color_test))
        # Max points
        train_min = min(data["train loss"])
        test_min = min(data["test loss"])
        # ATTENTION! this will only give you first occurrence
        train_min_index = data["train loss"].to_list().index(train_min)
        test_min_index = data["test loss"].to_list().index(test_min)

        fig.add_trace(go.Scatter(x=[train_min_index],
                                 y=[train_min],
                                 mode='markers',
                                 name='min value train',
                                 text=['{0:.2f}%'.format(train_min)],
                                 textposition="top center",
                                 marker_color=color_train))
        fig.add_trace(go.Scatter(x=[test_min_index],
                                 y=[test_min],
                                 mode='markers',
                                 name='min value test',
                                 text=['{0:.2f}%'.format(test_min)],
                                 textposition="top center",
                                 marker_color=color_test))
        annotations = []
        # Min annotations
        annotations.append(dict(xref="x", yref="y", x=train_min_index, y=train_min,
                                xanchor='left', yanchor='middle',
                                text='{0:.2f}%'.format(train_min),
                                font=dict(family='Arial',
                                          size=14),
                                showarrow=False, ay=-40))
        annotations.append(dict(xref="x", yref="y", x=test_min_index, y=test_min,
                                xanchor='left', yanchor='middle',
                                text='{0:.2f}%'.format(test_min),
                                font=dict(family='Arial',
                                          size=14),
                                showarrow=False, ay=-40))
        # Right annotations
        annotations.append(dict(xref='paper', x=0.95, y=data["train loss"].to_list()[-1],
                                xanchor='left', yanchor='middle',
                                text='{0:.2f}%'.format(data["train loss"].to_list()[-1]),
                                font=dict(family='Arial',
                                          size=16),
                                showarrow=False))
        annotations.append(dict(xref='paper', x=0.95, y=data["test loss"].to_list()[-1],
                                xanchor='left', yanchor='middle',
                                text='{0:.2f}%'.format(data["test loss"].to_list()[-1]),
                                font=dict(family='Arial',
                                          size=16),
                                showarrow=False))
        fig.update_layout(annotations=annotations,
                          title='Train vs Test loss',
                          xaxis_title='epochs',
                          yaxis_title='loss')
        if savefig:
            plotly.offline.plot(fig, filename=path + "/" + library + "_loss_" + file.replace(".csv", ".html"))
        elif showfig:
            fig.show()
    else:
        print("Warning: Unrecognized library to plot " + library)


def plot_acc(filename, savefig=True, showfig=True, library='plotly'):
    assert type(filename) == str
    path, file = os.path.split(filename)
    data = pd.read_csv(filename)
    if library == 'matplotlib':
        fig, ax = plt.subplots()
        ax.plot(range(len(data["train acc"])),
                data["train acc"],
                'o-',
                label='train acc')
        ax.plot(range(len(data["test acc"])),
                data["test acc"],
                '^-',
                label='test acc')
        fig.legend(loc="lower right")
        ax.set_ylabel("epochs")
        ax.set_xlabel("accuracy (%)")
        fig.suptitle("Train vs Test accuracy")
        if showfig:
            fig.show()
        if savefig:
            fig.savefig(path + "/" + library + "_acc_" + file.replace(".csv", ".png"))
    elif library == 'plotly':
        fig = go.Figure()
        color_train = 'rgb(255, 0, 0)'
        color_test = 'rgb(0, 255, 0)'
        assert len(data["train acc"]) == len(data["test acc"])
        x = list(range(len(data["train acc"])))
        fig.add_trace(go.Scatter(x=x,
                                 y=data["train acc"],
                                 mode='lines',
                                 name='train acc',
                                 line_color=color_train))
        fig.add_trace(go.Scatter(x=x,
                                 y=data["test acc"],
                                 mode='lines',
                                 name='test acc',
                                 line_color=color_test))
        # Add points
        fig.add_trace(go.Scatter(x=[x[-1]],
                                 y=[data["train acc"].to_list()[-1]],
                                 mode='markers',
                                 name='last value train',
                                 marker_color=color_train))
        fig.add_trace(go.Scatter(x=[x[-1]],
                                 y=[data["test acc"].to_list()[-1]],
                                 mode='markers',
                                 name='last value test',
                                 marker_color=color_test))
        # Max points
        train_max = max(data["train acc"])
        test_max = max(data["test acc"])
        # ATTENTION! this will only give you first occurrence
        train_max_index = data["train acc"].to_list().index(train_max)
        test_max_index = data["test acc"].to_list().index(test_max)

        fig.add_trace(go.Scatter(x=[train_max_index],
                                 y=[train_max],
                                 mode='markers',
                                 name='max value train',
                                 text=['{}%'.format(int(train_max * 100))],
                                 textposition="top center",
                                 marker_color=color_train))
        fig.add_trace(go.Scatter(x=[test_max_index],
                                 y=[test_max],
                                 mode='markers',
                                 name='max value test',
                                 text=['{}%'.format(int(test_max*100))],
                                 textposition="top center",
                                 marker_color=color_test))
        annotations = []
        # Max annotations
        annotations.append(dict(xref="x", yref="y", x=train_max_index, y=train_max,
                                xanchor='left', yanchor='middle',
                                text='{}%'.format(int(train_max * 100)),
                                font=dict(family='Arial',
                                          size=14),
                                showarrow=False, ay=-40))
        annotations.append(dict(xref="x", yref="y", x=test_max_index, y=test_max,
                                xanchor='left', yanchor='middle',
                                text='{}%'.format(int(test_max * 100)),
                                font=dict(family='Arial',
                                          size=14),
                                showarrow=False, ay=-40))
        # Right annotations
        annotations.append(dict(xref='paper', x=0.95, y=data["train acc"].to_list()[-1],
                                xanchor='left', yanchor='middle',
                                text='{}%'.format(int(data["train acc"].to_list()[-1]*100)),
                                font=dict(family='Arial',
                                          size=16),
                                showarrow=False))
        annotations.append(dict(xref='paper', x=0.95, y=data["test acc"].to_list()[-1],
                                xanchor='left', yanchor='middle',
                                text='{}%'.format(int(data["test acc"].to_list()[-1]*100)),
                                font=dict(family='Arial',
                                          size=16),
                                showarrow=False))
        fig.update_layout(annotations=annotations,
                          title='Train vs Test accuracy',
                          xaxis_title='epochs',
                          yaxis_title='accuracy (%)'
                          )
        if savefig:
            plotly.offline.plot(fig, filename=path + "/" + library + "_acc_" + file.replace(".csv", ".html"))
        elif showfig:
            fig.show()
    else:
        print("Warning: Unrecognized library to plot " + library)


def plot_loss_and_acc(filename, savefig=True, showfig=True, library='plotly'):
    plot_loss(filename, savefig, showfig, library)
    plot_acc(filename, savefig, showfig, library)


"""
Confusion Matrix
----------------
Given results and labels directly
"""


def plot_confusion_matrix(data, filename=None, library='plotly', axis_legends=None, showfig=False):
    if library == 'seaborn':
        fig, ax = plt.subplots()
        sns.heatmap(data,
                    annot=True,
                    linewidths=.5,
                    cbar=True,
                    )
        if filename is not None:
            fig.savefig(filename)
    elif library == 'plotly':
        z = data.values.tolist()
        if axis_legends is None:
            y = [str(j) for j in data.axes[0].tolist()]
            x = [str(i) for i in data.axes[1].tolist()]
        else:
            y = []
            x = []
            for j in data.axes[0].tolist():
                if isinstance(j, int):
                    y.append(axis_legends[j])
                elif isinstance(j, str):
                    y.append(j)
                else:
                    print("WTF?! should never have arrived here")
            for i in data.axes[1].tolist():
                if isinstance(i, int):
                    x.append(axis_legends[i])
                elif isinstance(i, str):
                    x.append(i)
                else:
                    print("WTF?! should never have arrived here")
        # fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y))
        fig = ff.create_annotated_heatmap(z, x=x, y=y)
    if showfig:
        fig.show()


def sparse_confusion_matrix(y_pred_np, y_label_np, filename=None, axis_legends=None):
    y_pred_pd = pd.Series(y_pred_np, name='Predicted')
    y_label_pd = pd.Series(y_label_np, name='Actual')
    df = pd.crosstab(y_label_pd, y_pred_pd, rownames=['Actual'], colnames=['Predicted'], margins=True)
    plot_confusion_matrix(df, filename, library='plotly', axis_legends=axis_legends)
    return df


def categorical_confusion_matrix(y_pred_np, y_label_np, filename=None, axis_legends=None):
    return sparse_confusion_matrix(np.argmax(y_pred_np, axis=1), np.argmax(y_label_np, axis=1), filename, axis_legends)


class Plotter:

    def __init__(self, path):
        assert os.path.exists(path)
        self.path = Path(path)
        self.pandas_list = []
        self.labels = []

    def _csv_to_pandas(self):
        for file in os.listdir(self.path):
            if file.endswith(".csv"):
                # print(file)
                self.pandas_list.append(pd.read_csv(self.path / file))
                self.labels.append(os.path.splitext(file)[0])

    def reload_data(self):
        self._csv_to_pandas()

    def plot_everything(self, reload=False, library='matplotlib', showfig=False, savefig=True):
        if reload:
            self._csv_to_pandas()
        assert len(self.pandas_list) != 0
        for key in self.pandas_list[0]:
            self.plot_key(key, reload=False, library=library, showfig=showfig, savefig=savefig)

    def plot_key(self, key='loss', reload=False, library='matplotlib', showfig=False, savefig=True):
        if reload:
            self._csv_to_pandas()
        if library == 'matplotlib':
            self._plot_matplotlib(key=key, showfig=showfig, savefig=savefig)
        elif library == 'plotly':
            self._plot_plotly(key=key, showfig=showfig, savefig=savefig)
        else:
            print("Warning: Unrecognized library to plot " + library)

    def _plot_matplotlib(self, key='loss', showfig=False, savefig=True):
        fig, ax = plt.subplots()
        title = None
        for i, data in enumerate(self.pandas_list):
            if key in data:
                ax.plot(data[key], 'o-', label=self.labels[i])
                if title is not None:
                    title += " vs. " + self.labels[i]
                else:
                    title = self.labels[i]
        title += " " + key
        fig.legend(loc="upper right")
        ax.set_ylabel(key)
        ax.set_xlabel("step")
        ax.set_title(title)
        if showfig:
            fig.show()
        if savefig:
            fig.savefig(str(self.path) + key + ".png")

    def _plot_plotly(self, key='loss', showfig=False, savefig=True, func=min):
        fig = go.Figure()
        colors = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)']  # TODO: This only works for 2 cases, no 3
        annotations = []
        title = None
        for i, data in enumerate(self.pandas_list):
            if key in data:
                if title is not None:
                    title += " vs. " + self.labels[i]
                else:
                    title = self.labels[i]
                x = list(range(len(data[key])))
                fig.add_trace(go.Scatter(x=x, y=data[key], mode='lines', name=self.labels[0], line_color=colors[i]))
                # Add points
                fig.add_trace(go.Scatter(x=[x[-1]],
                                         y=[data[key].to_list()[-1]],
                                         mode='markers',
                                         name='last value',
                                         marker_color=colors[i]))
                # Max/min points
                func_value = func(data[key])
                # ATTENTION! this will only give you first occurrence
                func_index = data[key].to_list().index(func_value)
                if func_index != len(data[key])-1:
                    fig.add_trace(go.Scatter(x=[func_index],
                                             y=[func_value],
                                             mode='markers',
                                             name=func.__name__,
                                             text=['{0:.2f}%'.format(func_value)],
                                             textposition="top center",
                                             marker_color=colors[i]))
                    # Min annotations
                    annotations.append(dict(xref="x", yref="y", x=func_index, y=func_value,
                                            xanchor='left', yanchor='middle',
                                            text='{0:.2f}'.format(func_value),
                                            font=dict(family='Arial',
                                                      size=14),
                                            showarrow=False, ay=-40))
                # Right annotations
                annotations.append(dict(xref='paper', x=0.95, y=data[key].to_list()[-1],
                                        xanchor='left', yanchor='middle',
                                        text='{0:.2f}'.format(data[key].to_list()[-1]),
                                        font=dict(family='Arial',
                                                  size=16),
                                        showarrow=False))
        fig.update_layout(annotations=annotations,
                          title=title,
                          xaxis_title='epochs',
                          yaxis_title=key)
        if savefig:
            plotly.offline.plot(fig, filename=str(self.path) + key + ".html")
        elif showfig:
            fig.show()


# class MonteCarloPlotter(Plotter):

  #   def plot_histogram(self):







if __name__ == "__main__":
    plotter = Plotter("./log/2020/2February/21Friday/run-20h24m21")
    plotter.plot_everything(library="plotly", reload=True, showfig=True, savefig=True)
    # res = get_histogram_results('./results')
    # res = get_pandas_mean_for_each_class(res)
    # plot_loss_and_acc("/home/barrachina/Documents/cvnn/log/CVNN_testing/run-20200127140842/CVNN_testing.csv"
    # , visualize=True)
    # set_trace()

__author__ = 'J. Agustin BARRACHINA'
__version__ = '0.0.24'
__maintainer__ = 'J. Agustin BARRACHINA'
__email__ = 'joseagustin.barra@gmail.com; jose-agustin.barrachina@centralesupelec.fr'
