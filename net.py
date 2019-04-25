#!/usr/bin/env python3
from pprint import pprint
from collections import defaultdict
from matplotlib.ticker import NullLocator

import matplotlib.pyplot as plt
import seaborn           as sns
import networkx          as nx

import pandas

def read_alarm_data():
    propData  = pandas.read_csv('propagation.csv')
    alarmData = pandas.read_csv('smoothed_alarm_strengths.csv')
    alarmTSeries = []
    max_seconds = max(propData['TimeForAlarm'])
    for second in range(1, max_seconds + 1):
        antDict = dict()
        alarmSecondData = alarmData[
                          (alarmData.Frame < (second + 1) * 30) &
                          (alarmData.Frame > (second) * 30)].iloc[0]
        for i in range(1, 62):
            antDict[i] = alarmSecondData['V' + str(i)]
        alarmTSeries.append(antDict)
    return alarmTSeries

def read_network():
    propData = pandas.read_csv('propagation.csv')

    interactions     = []
    currentDict      = dict()
    time_index       = 0
    seen             = defaultdict(lambda : 0)

    for index, row in propData.iterrows():
        time = row.TimeForAlarm
        if time_index < time:
            for i in range(time_index + 1, time):
                interactions.append(dict())
            time_index = time
            interactions.append(currentDict)
            currentDict = dict()
        a, b = row.AlarmedFrom, row.Alarmed
        seen[a] += 1; seen[b] += 1;
        currentDict[a] = b
    return seen, interactions

def plot_network(interval=None, filename=None):
    seen, interactions = read_network()
    alarmSeries        = read_alarm_data()

    G = nx.Graph()
    colorMap = []
    x = 0
    label = True
    metaseen = set()
    exclude_passive = False
    binary_color = False
    order_type = 'interactions'
    order_type = 'alarm_strength'
    order_type = 'initial_alarm_strength'
    order_type = 'vanilla'

    if order_type == 'vanilla':
        orderer = lambda x : x
    elif order_type == 'interactions':
        orderer = lambda x : seen[x]
    elif order_type == 'alarm_strength':
        orderer = lambda x : sum(s[x] for s in alarmSeries)
    elif order_type == 'initial_alarm_strength':
        orderer = lambda x : alarmSeries[0][x]

    ordering = [t[0] for t in
                     sorted(((i, orderer(i)) for i in range(1, 62)),
                            key=lambda t : t[1],
                            reverse=True)]

    blackLabels = dict()

    for time_index, data in enumerate(interactions):
        if interval is None or time_index in interval:
            y = 0.0
            lat = x * 61
            for i in ordering:
                if not exclude_passive or seen[i] > 0:
                    #print(lat + i)
                    G.add_node(lat + i, pos=(x * 50, y))
                    color = alarmSeries[time_index][i]
                    if binary_color:
                        color = 1.0 if color > 0.74 else 0.5
                    blackLabels[lat + i] = str(i)
                    colorMap.append(color)
                    metaseen.add(lat + i)
                    y += 100
            for k, v in data.items():
                if (interval is None and (x + 1) * 61 + v < 1769) or \
                   ((x + 1) * 61 + v < min(176, (max(interval) - 2) * 61)):
                       if (x + 1) * 61 + v == 220:
                           print((x + 1) * 61 + v)
                           1/0
                       G.add_edge(lat + k, (x + 1) * 61 + v)
            x += 1
            if x == 28 and interval is None:
                break

    fsize = 5
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, node_color=colorMap, cmap=plt.cm.Reds, node_size=10)
    if label:
        pos = {k : (x - 1.5, y) for k, (x, y) in pos.items()}
        nx.draw_networkx_labels(G, pos, labels=blackLabels, font_size=fsize)
    plt.axis('off')
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
    hspace = 0, wspace = 0)
    #plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(NullLocator())
    plt.gca().yaxis.set_major_locator(NullLocator())
    if filename is not None:
        plt.savefig(filename, dpi=300)
        plt.clf()
    else:
        plt.show()

def main():
    plot_network()

if __name__ == '__main__':
    main()
