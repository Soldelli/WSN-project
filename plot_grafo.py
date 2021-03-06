import matplotlib.pyplot as plt
import numpy as np


########################################################################################################################
# This function can be used to plot the random graph, storage nodes and their edges will be shows as grey dots and lines.
# Sensors nodes and their edges will be shown as red dots and lines.
########################################################################################################################

def plot_grafo(node_list, n , k , sensors_indexes, L):
    ii=-1
    x1 = np.zeros(n)
    y1 = np.zeros(n)

    plt.figure(figsize=(L, L))

    for i in xrange(n):
        ii += 1
        x1[ii] = node_list[i].X
        y1[ii] = node_list[i].Y
        for iii in xrange(node_list[i].node_degree):
            #color = '#eeefff'
            xx = [node_list[i].X, node_list[i].neighbor_list[iii].X]
            yy = [node_list[i].Y, node_list[i].neighbor_list[iii].Y]
            plt.plot(xx,yy,color='grey')

    x2 = np.zeros(len(sensors_indexes))
    y2 = np.zeros(len(sensors_indexes))
    ii = -1
    for i in sensors_indexes:
        ii += 1
        x2[ii] = node_list[i].X
        y2[ii] = node_list[i].Y
        for iii in xrange(node_list[i].node_degree):
            xx = [node_list[i].X, node_list[i].neighbor_list[iii].X]
            yy = [node_list[i].Y, node_list[i].neighbor_list[iii].Y]
            plt.plot(xx,yy,color='red')

    plt.plot(x1, y1, color='grey', linestyle='', marker='o',markersize=10.0, markeredgewidth=1.0)
    plt.plot(x2, y2, color='red', linestyle='', marker ='o',markersize=10.0, markeredgewidth=1.0,
    markerfacecolor='red', markeredgecolor='black')
    plt.axis('off')
    plt.xlim(-0.5, L*1.05)
    plt.ylim(-0.5, L*1.05)
    plt.savefig('Immagini/Grafo/Grafo_n=' + str(n) + '_k=' + str(k) + '.pdf', dpi=150, transparent=True)

