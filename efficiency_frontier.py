'''
Module will calculate an efficency frontier.
'''
import enum
import matplotlib.pyplot as plt
import pandas as pd
import copy


class DataIndex(enum.IntEnum):
    Label = 0
    Benefit = 1
    Cost = 2
    ICER = 3


def _get_icers(data):
    icers = []
    for strategy in range(1, len(data)):
        icers.append(
            (data[strategy][DataIndex.Cost] - data[strategy
                                                   - 1][DataIndex.Cost]) /
            (data[strategy][DataIndex.Benefit] - data[strategy
                                                      - 1][DataIndex.Benefit]))
    return icers


def _drop_icer_dominated_strategies(data):

    while True:
        end = False
        icers = _get_icers(data)
        # length of ICER's is 1 less than the length of data
        for index in range(len(icers)):
            if index == len(icers) - 1:
                end = True
                break
            else:
                if icers[index] > icers[index + 1]:
                    # This is a little tricky, but assume we have icers
                    # like this:
                    # 2 vs 1 -> 100
                    # 3 vs 2 -> 300
                    # 4 vs 3 --> 200
                    # Then because 3 vs 2 is greater than 4 vs 3, we delete
                    # the third strategy which is index 1 in our ICERs BUT is
                    # actually index 2 in our data
                    del data[index + 1]
                    # Restart from the top
                    break
        if end is True:
            # Append ICER's
            data[0].append("N/A")
            for i in range(1, len(data)):
                data[i].append(icers[i - 1])
            break


def _drop_dominated_strategies(data):
    while True:
        end = False
        for strategy in range(len(data)):
            if strategy == len(data) - 1:
                end = True
                break
            else:
                if (data[strategy][DataIndex.Benefit] >=
                        data[strategy + 1][DataIndex.Benefit]
                        and data[strategy][DataIndex.Cost] <
                        data[strategy + 1][DataIndex.Cost]):
                    # Dominated
                    del data[strategy + 1]
                    # Restart from the top
                    break
        if end is True:
            break


def _get_data_from_csv(path, header_in_file):
    data = []
    f = open(path, 'r')
    got_header = True
    if header_in_file is True:
        got_header = False
    for line in f:
        if got_header is False:
            got_header = True
        else:
            split_line = line.split(',')
            row = []
            row.append(split_line[0])
            row.append(float(split_line[1]))
            row.append(float(split_line[2]))
            data.append(row)
    return data


def _get_optimal(data, threshold):
    last_index = len(data) - 1
    while last_index > 0:
        if data[last_index][DataIndex.ICER] < threshold:
            return data[last_index].copy()
        last_index -= 1
    return data[0].copy()


def _data_to_csv(data, header, path):
    df = pd.DataFrame(data, columns=header)
    df.to_csv(path, index=False)


def calculate_frontier(
        data=None,
        read_in_data=False,
        data_header_in_csv=True,
        path_to_data=None,
        threshold=100000,
        print_original=False,
        path_to_print_original='original_data.csv',
        print_frontier_strategies=True,
        path_to_frontier_output='frontier_strategies.csv',
        print_graph=True,
        path_to_graph='graph',
        title='Efficiency Frontier',
        invert_graph=True,  # Standard way of looking at it
        list_frontier=True,
        mark_optimal=True,
        ICER_digits=2):
    '''
    Input data in format of [[strategy labels, benefits, costs]]; a
    n x 3 dimensional array where n is the number of strategies and each row
    has a label (string), a benefit (double), and a cost (double). Or,
    write the analagous in a CSV file and point to the file and whether or not
    there is a header.
    '''
    if read_in_data:
        data = _get_data_from_csv(path_to_data, data_header_in_csv)

    if print_original:
        _data_to_csv(data, ['Label', 'Benefit', 'Cost'],
                     path_to_print_original)

    # Scatterplot everything
    if print_graph:
        plt.style.use('bmh')
        fig, ax = plt.subplots(nrows=1, ncols=1, dpi=300, figsize=(15, 7.5))
        plt.title(title)
        all_benefit = [strategy[DataIndex.Benefit] for strategy in data]
        all_cost = [strategy[DataIndex.Cost] for strategy in data]
        if invert_graph:
            plt.scatter(all_cost, all_benefit, s=3.25, c='b', label='All Data')
        else:
            plt.scatter(all_benefit, all_cost, s=3.25, c='b', label='All Data')

    # sort data inplace by the cost and benefit values
    data.sort(
        key=
        lambda strategy: (strategy[DataIndex.Benefit], strategy[DataIndex.Cost])
    )

    # Then, iteratively go through dataframe dropping strategies that are
    # dominated; i.e. strategies where the cost value is lower than the one
    # before it (we already know that the benefit value is higher)

    _drop_dominated_strategies(data)

    # Now comes a tricky part. We calculate ICERs between adjacent pairs and
    # drop the strategies where the ICER is greater than the next pair

    _drop_icer_dominated_strategies(data)

    # Final headers and dataframes

    df = pd.DataFrame(data, columns=['Label', 'Benefit', 'Cost', 'ICER'])
    if print_frontier_strategies:
        _data_to_csv(data, ['Label', 'Benefit', 'Cost', 'ICER'],
                     path_to_frontier_output)
    if print_graph:

        # Plot the optimal point
        if mark_optimal:
            optimal_strategy = _get_optimal(data, threshold)
            if invert_graph:
                plt.scatter(
                    optimal_strategy[DataIndex.Cost],
                    optimal_strategy[DataIndex.Benefit],
                    s=200.25,
                    c='cyan',
                    label='Optimal Strategy')
            else:
                plt.scatter(
                    optimal_strategy[DataIndex.Benefit],
                    optimal_strategy[DataIndex.Cost],
                    s=200.25,
                    c='cyan',
                    label='Optimal Strategy')

        if invert_graph:
            plt.plot(
                df['Cost'], df['Benefit'], 'r--', label='Efficiency Frontier')
        else:
            plt.plot(
                df['Benefit'], df['Cost'], 'r--', label='Efficiency Frontier')
        plt.legend()

        # Add on a textbox that includes the dominant strategy
        if list_frontier:
            text_for_textbox = ""
            if mark_optimal:
                text_for_textbox += "Optimal Strategy - "
                text_for_textbox += optimal_strategy[DataIndex.Label] + "\n\n\n"
            text_for_textbox += "Strategies on Frontier\n"
            for strategy in data:
                text_for_textbox += "\n" + strategy[DataIndex.Label]
                text_for_textbox += " | ICER : "
                icer = strategy[DataIndex.ICER]
                if icer != 'N/A':
                    icer = str(round(float(icer), ICER_digits))
                text_for_textbox += icer
            props = dict(boxstyle='square', facecolor='white', alpha=0.5)
            if invert_graph:
                loc = (0.65, 0.35)
            else:
                loc = (0.35, 0.55)
            fig.text(
                *loc,
                text_for_textbox,
                transform=ax.transAxes,
                size='small',
                verticalalignment='center',
                bbox=props)
        plt.savefig(path_to_graph, dpi=300)
        plt.close()
        plt.clf()
    return df