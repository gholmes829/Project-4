#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from kmeans import kmeans

k=0

def main():
	plt.style.use(["dark_background"])
	plt.rc("grid", linestyle="--", color="white", alpha=0.5)
	plt.rc("axes", axisbelow=True)
	
	# generating test data
	d0, d1 = (5, 2)
	scale = 1  # how much points should deviate from center
	if d1 == 3:
		c0 = np.full((d0, d1), [1.5, 3.5, 4]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65, 3]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15, 3]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65, 4]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5, 2]) + unitNoise(d0, d1)*scale
	elif d1 == 2:
		c0 = np.full((d0, d1), [1.5, 3.5]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5]) + unitNoise(d0, d1)*scale
	elif d1 == 4:
		c0 = np.full((d0, d1), [1.5, 3.5, 4, 1]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65, 3, -5.15]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15, 3, -5.3]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65, 0, -5.15]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5, 2, -5.2]) + unitNoise(d0, d1)*scale
	elif d1 == 5:
		c0 = np.full((d0, d1), [1.5, 3.5, 4, 1, 1]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65, 3, -5.15, 1.1]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15, 3, -5.3, 1.2]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65, 0, -5.15, -1]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5, 2, -5.2, 5]) + unitNoise(d0, d1)*scale
	clusters = []
	clusters.append(c0)
	clusters.append(c1)
	clusters.append(c2)
	clusters.append(c3)
	clusters.append(c4)
	data = np.concatenate(clusters, axis=0)
	standardized = (data-data.mean(axis=0))/data.std(axis=0)
	clusters = kmeans(standardized, k)

def unitNoise(d0, d1):
		noise =  np.random.randn(d0, d1)
		minimum = noise.min()
		noise-=minimum
		maximum = noise.max()
		return (noise/maximum)*2-1

def plot(x, y):
		plt.figure()
		plt.grid()
		plt.plot(x, y, 'o', c="red", mec="white", ms=7.5, zorder=2)
		plt.xlabel("x")
		plt.ylabel("y")
		
		plt.show()	

if __name__ == "__main__":
	main()
