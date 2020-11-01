#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from kmeans import kmeans

k=4

def main():
	plt.style.use(["dark_background"])
	plt.rc("grid", linestyle="--", color="white", alpha=0.5)
	plt.rc("axes", axisbelow=True)
	
	# generating test data
	d0, d1 = (150, 2)
	scale = 5  # how much points should deviate from center
	c0, c1 = np.full((d0, d1), [1.5, 3.5]) + unitNoise(d0, d1)*scale, np.full((d0, d1), [-1, -4.25]) + unitNoise(d0, d1)*scale  # modify values to adjust center
	
	data = np.concatenate((c0, c1), axis=0)
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
