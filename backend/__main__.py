#!/usr/bin/env python3
import numpy as np
from clustering import Clusters
import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def getCurrent() -> str:
     return os.getcwd()
    
def getParent(path: str) -> str:
    return os.path.dirname(path)   
    
def getChild(path: str, target: str) -> str:
    return os.path.join(path, target)

def standardized(arr):
    return (arr-arr.mean(axis=0))/arr.std(axis=0)

def main():
    print("Running...")    
 
    current = getCurrent()
    parent = getParent(current)
            
    filePath = getChild(parent, 'playlist.json')
    spotify = json.load(open(filePath))
    
    amount = spotify["Playlist"]
    a=len(amount)
    print(a)
    newDict = {}
    i=0
    
    for i in range(a):
        list = []
        temp = spotify["Playlist"][i]
        x = temp["ID"]
        newDict[x] = None
        list.append(temp["acousticness"])
        list.append(temp["danceability"]) 
        list.append(temp["energy"]) 
        """list.append(temp["instrumentalness"]) 
        list.append(temp["key"]) 
        list.append(temp["liveness"]) 
        list.append(temp["loudness"]) 
        list.append(temp["speechiness"]) 
        list.append(temp["tempo"]) 
        list.append(temp["valence"])"""

        newDict[x] = list
        
    newList = []
    for key in newDict:
        newList.append(newDict[key])
    
    converted = np.array(newList)
    std = standardized(converted)
    clusters = Clusters(std)
    centroids = clusters.keys()
    clusters.printInfo()
    
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
    
    plt.figure()
    ax = plt.axes(projection="3d")
    ax.scatter3D(centroids[:,0], centroids[:,1], centroids[:,2], '*', c="blue", zorder=3, label="final")

    c=0
    for centroid in clusters:
        data = clusters[centroid]
        ax.scatter3D(data[:,0], data[:,1], data[:,2], c=colors[c], zorder=1)
        c+=1
     
    d, s = clusters.orderedData, clusters.orderedScores
    threshold = 0.7  # change this value to change 
    a, b = d[:int(threshold*len(d))], d[int(threshold*len(d)):]
    
    plt.figure()
    ax = plt.axes(projection="3d")
    ax.scatter3D(0, 0, 0, '*', c="green", zorder=1)
    ax.scatter3D(a[:,0], a[:,1], a[:,2], 'o', c="blue", zorder=1)
    ax.scatter3D(b[:,0], b[:,1], b[:,2], 'o', c="red", zorder=1)
    plt.show()

    print("Done!")
    
if __name__ == "__main__":
    main()

