#!/usr/bin/env python3

import numpy as np
from clustering import Clusters
import matplotlib.pyplot as plt

     
def main():
    """
    Post: Runs the main function that prints out the results of the test
    """ 
    #k=None

    print("Testing...")

    if checkRange() == 1:
        print("Check if scores range from 0 to 100: PASSED")
    else:
        print("Check if scores range from 0 to 100: FAILED")
    if checkZero() == 1:
        print("Check for k = 0: PASSED")
    else:
        print("Check for k = 0: NEGATIVE")
    if checkNegative() == 1:
        print("Check for k < 0: PASSED")
    else:
        print("Check for k < 0: NEGATIVE")
    if checkEmpty() == 1:
        print("Check for empty clusters : PASSED")
    else:
        print("Check for empty clusters: NEGATIVE")
        
    #exampleCluster(data, k)
    # generating test data

def checkZero():
    """
    Post: Function tests when k = 0
    """
    data = generateClusters(50, 3, 1, 3)
    try:
        Clusters(data, 0)
    except ValueError:
        return True
    return False


def checkNegative():
    """
    Post: Function tests when k < 0
    """
    data = generateClusters(50, 3, 1, 3)
    try:
        Clusters(data, -5)
    except ValueError:
        return True
    return False


def checkRange():
    """
    Post: Function tests the scores to see if they are between 0-100
    """
    data = generateClusters(50, 3, 1, 3)
    myClusters = Clusters(data, 2)
    scores = myClusters.orderedScores
    l = len(scores)

    count = 0
    try:
        for i in range(l):
            if(scores[i] <= 100 and scores[i] >= 0):
                count += 1
        Clusters(data, 2)
    except count == 150:
        return False
    return True
 
  
def checkEmpty():
    """
    Post: Function tests if generateClusters function is given 0 clusters
    """ 
    try:
        data = generateClusters(50, 3, 1, 0)
        Clusters(data, 1)
    except ValueError:
        return True
    return False
     
def generateClusters(density, dimension, scale, numClust):
    """
    Parameters: numClust is the number of clusters. Density in the tightness of the clusters. 
    Dimension is if its 2d, 3d, etc. Scale determines how much will deviate
    
    Post: The function will create clusters with the information and the data that is given. These clusters
    will help determine what songs fit best with the playlist and what dont
    """
    d0, d1 = (density, dimension) 
    if d1 == 2:
        clusters= [
        np.full((d0, d1), [1.5, 3.5]) + unitNoise(d0, d1)*scale,  # modify values to adjust center
        np.full((d0, d1), [-0.25, -0.65]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-3.5, 2.15]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-1.1, 5.65]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-0.5, 2.5]) + unitNoise(d0, d1)*scale,
        ]
    elif d1 == 3:
        clusters = [
        np.full((d0, d1), [1.5, 3.5, 4]) + unitNoise(d0, d1)*scale, # modify values to adjust center
        np.full((d0, d1), [-0.25, -0.65, 3]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-3.5, 2.15, 3]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-1.1, 5.65, 4]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-0.5, 2.5, 2]) + unitNoise(d0, d1)*scale,
        ]
    elif d1 == 4:
        clusters = [
        np.full((d0, d1), [1.5, 3.5, 4, -5.2]) + unitNoise(d0, d1)*scale,  # modify values to adjust center
        np.full((d0, d1), [-0.25, -0.65, 3, -5.15]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-3.5, 2.15, 3, -5.3]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-1.1, 5.65, 0, -5.15]) + unitNoise(d0, d1)*scale,
        np.full((d0, d1), [-0.5, 2.5, 2, -5.2]) + unitNoise(d0, d1)*scale,
        ] 
        
    finalClusters = []
    for i in range(numClust):
        finalClusters.append(clusters[i])
    
    data = np.concatenate(finalClusters, axis=0)
    standardized = (data-data.mean(axis=0))/data.std(axis=0)
    return standardized

def exampleCluster(data, k):  # testing kmeans
    plt.style.use(["dark_background"])
    plt.rc("grid", linestyle="--", color="white", alpha=0.5)
    plt.rc("axes", axisbelow=True)

    clusters = Clusters(data, k)
    print("Completed!\n")
    clusters.printInfo()
    print()

    centroids = clusters.keys()

    d = clusters.orderedData
    threshold = 0.7  # change this value to change 
    a, b = d[:int(threshold*len(d))], d[int(threshold*len(d)):]
    
    colors = {
        0: "green",
        1: "red",
        2: "orange",
        3: "purple",
        4: "cyan",
        5: "magenta",
        6: "pink",
        7: "yellow",
    }
    
    if(data.shape[1] < 4):
         print("Plotting...")
    if data.shape[1] == 2:
        plt.figure()
        plt.grid()
        plt.plot(centroids[:,0], centroids[:,1], '*', c="blue", mec="white", ms=20, zorder=3, label="final")
        plt.legend(loc="upper right")

        c=0
        for centroid in clusters:
            data = clusters[centroid]
            plt.plot(data[:,0], data[:,1], 'o', c=colors[c], mec="white", ms=7.5, zorder=1)
            c+=1

        plt.xlabel("x")
        plt.ylabel("y")

        plt.figure()
        plt.grid()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.plot(centroids[:,0], centroids[:,1], '*', c="green", mec="white", ms=15, zorder=3, label="final")
        plt.plot(clusters.center[0], clusters.center[1], 's', c="purple", mec="white", ms=15, zorder=1)
        plt.plot(a[:,0], a[:,1], 'o', c="blue", mec="white", ms=7.5, zorder=1)
        plt.plot(b[:,0], b[:,1], 'o', c="red", mec="white", ms=7.5, zorder=1)
    
    elif data.shape[1] == 3:
        plt.figure()
        ax = plt.axes(projection="3d")
        ax.scatter3D(centroids[:,0], centroids[:,1], centroids[:,2], '*', c="blue", zorder=3, label="final")

        c=0
        for centroid in clusters:
            data = clusters[centroid]
            ax.scatter3D(data[:,0], data[:,1], data[:,2], c=colors[c], zorder=1)
            c+=1
        
        plt.figure()
        ax = plt.axes(projection="3d")
        ax.scatter3D(0, 0, 0, '*', c="green", zorder=1)
        ax.scatter3D(a[:,0], a[:,1], a[:,2], 'o', c="blue", zorder=1)
        ax.scatter3D(b[:,0], b[:,1], b[:,2], 'o', c="red", zorder=1)
        
    if data.shape[1] > 3:
        for i, centroid in enumerate(clusters):
            data = clusters[centroid]
            print("Cluster "+str(i)+": "+str(len(data)))
    
    if data.shape[1] <= 3:
        plt.show()

    print("Done!")

def unitNoise(d0, d1):
        noise =  np.random.randn(d0, d1)
        minimum = noise.min()
        noise-=minimum
        maximum = noise.max()
        return (noise/maximum)*2-1    

if __name__ == "__main__":
    main()
