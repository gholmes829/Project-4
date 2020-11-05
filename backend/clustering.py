"""
File: clustering.py
Author: Grant Holmes
Date: 11/04/20
Description: Uses extension of kmeans clustering alongside silhouette coefficient scoring to organize nth dimensional data into k clusters. Can also auto solve for k.
"""
import numpy as np

class Clusters(dict):
	"""
	Uses kmeans clustering and silhoutte coefficient scoring to find clusters amongst data.
	"""
	def __init__(self, data: np.ndarray, k: int=None, maxK: int=10, maxIterations: int=50, samples: int=10, alpha: float=0.85, accuracy: int=4) -> None:
		"""
		data: nth dimensional data to be clustered.
		k: target number of clusters. If k=None, k will be automatically selected.
		maxK: the maximum value of k that can be automatically selected.
		maxIterations: the maximum number of iterations _kmeans will use to try to reach convergence.
		samples: the number of configurations that will be generated to select.
		alpha: learning rate.
		accuracy: tolerance for _kmeans convergence.
		"""
		if not (k is None or k>=0):
			raise ValueError("K must be greater than or equal to zero")
		if not (data.shape[0] > 1):
			raise ValueError("Data must have greater that one point")

		super().__init__(self)

		# public attributes
		self.data = data
		self.k, self.maxK = k, maxK
		self.alpha = alpha
		self.accuracy = accuracy
		self.partitionQuality = 0

		self.orderedData = None
		self.orderedScores = None
		
		self.rawScoreMin, self.rawScoreMax = None, None
		self.rawScoreAvg = None
		self.scoreAvg = None

		self.maxIterations = maxIterations
		self.samples = samples
		self.autoSolve = k is None

		# data attributes
		self._center = self.data.mean(axis=0)
		self._bounds = np.zeros((self.data.shape[1], 2))

		for dimension in range(len(self._bounds)):
			self._bounds[dimension][0] = self.data[:,dimension].min()
			self._bounds[dimension][1] = self.data[:,dimension].max()

		self._ranges = np.diff(self._bounds).flatten()

		space = np.zeros((2, self.data.shape[1]))
		for dimension in range(len(self._bounds)):
			space[1][dimension] = self._ranges[dimension]
			
		self._range = self.dist(space[0], space[1])
		
		self._convergenceLimit = 1*(10**(-1*self.accuracy))
		self._silhouetteThreshold = 0.0375
		
		# state attributes
		self._dp = 0
		self._prevIteration = {}
		self._isAssigned = False
		self._solved = False

		# evaluation attributes
		self._silhouettes = {}
		
		# solving and generating scores
		self._solve()
		self._generateScores()
			
	def keys(self) -> np.ndarray:  # return centroid positions
		"""
		Returns np.array of centroid positions 
		"""
		return np.array([np.frombuffer(centroid) for centroid in super().keys()])

	def items(self) -> list:
		"""
		Returns key, value where key is centroid position and value is array of points assigned to centroid.
		"""
		return [(np.frombuffer(centroid), self._getPoints(centroid)) for centroid, points in super().items()]

	@staticmethod
	def dist(pt1: np.ndarray, pt2: np.ndarray) -> np.float64:
		"""
		Returns euclidean distance of pt1 and pt2.
		"""
		return np.sqrt(np.sum((pt2-pt1)**2))

	@staticmethod
	def optimizedDist(pt1: np.ndarray, pt2: np.ndarray) -> np.float64:
		"""
		Returns (euclidean distance)^2 of pt1 and pt2.
		"""
		return np.sum((pt2-pt1)**2)

	@staticmethod
	def rand(low: float, high: float) -> np.float64:
		"""
		Returns random float between low and high from uniform distribution.
		"""
		return np.random.uniform(low, high)

	def _solve(self) -> None:
		"""
		Pre: not already solved.
		Post: becomes solved.
		Solves to produce clusters from data.
		"""
		if self.k is not None:
			self._singleSolve()
		else:
			self._autoSolve()

		self._solved = True

	def _singleSolve(self) -> None:
		"""
		Pre: k!=None.
		Solves to produce clusters from data if k selected. 
		"""
		optimal = self._optimalPartition(self.k)
		self._revert(optimal)

	def _autoSolve(self) -> None:
		"""
		Pre: k==None.
		Solves to produce clusters from data if k not selected by computing silhouette coefficients.
		"""
		pivot = None
		optimal = None

		for k in range(2, self.maxK+1):  # testing configurations for values of k
			if k > 2:  # store current configuration as previous
				self._prevIteration = optimal
				
			optimal = self._optimalPartition(k)
			self._silhouettes[k] = self._silhouette(optimal)

			if k > 2:
				dScore = (self._silhouettes[k-1] - self._silhouettes[k])
				if dScore <= 0:  # if new score is better than prev score
					if pivot is not None and (pivot-self._silhouettes[k]) <= 0:  # if pivot is set and new score is better than or euqal to pivot score
						pivot = None
					if k==self.maxK:
						self._simplify()
						self.k = k
						self.partitionQuality = self._silhouettes[k]
				elif dScore <= self._silhouetteThreshold and (pivot is None or (pivot-self._silhouettes[k]) <= self._silhouetteThreshold):  # new score is worse but within tolerance
					if pivot is None:
						pivot = self._silhouettes[k-1]
					if k==self.maxK:
						self._simplify()
						self.k = k-1
						self.partitionQuality = self._silhouettes[k-1]
				else:  # new score is worse and exceeds tolerance
					self._revert(self._prevIteration)
					self.k = k-1
					self.partitionQuality = self._silhouettes[k-1]
					break

	def _optimalPartition(self, k: int) -> dict:
		"""
		k: number of clusters.
		Gets self.sample number of kmeans configurations and returns the optimal configuration.
		"""
		samples = []
		for i in range(self.samples):
			self.clear()
			self._kmeans(k)
			samples.append(self._simpleCopy())
		
		initialized = False
		optimal, bestCost = None, 0
		
		for i in range(len(samples)):
			cost = self._cost(samples[i])
			if cost == -1:
				continue
				
			elif not initialized:
				optimal, bestCost = samples[i], cost
				initialized = True
			elif cost <= bestCost:
				optimal, bestCost = samples[i], cost
		return optimal

	def _cost(self, partition: dict) -> float:
		"""
		partition: dictionary of centroids and assigned points.
		Computes cost of kmeans partition using average dist bt cluster and pts and max dist bt cluster and points.
		"""
		totalDist = 0
		maxDist = 0
		ptCount = 0
		
		for bufferCentroid, points in partition.items():
			size = len(points)
			ptCount += size
			if size == 0:
				return -1
			centroid = np.frombuffer(bufferCentroid)
			for pt in points:
				dist = Clusters.optimizedDist(pt, centroid)
				totalDist+=dist
				if dist > maxDist:
					maxDist = dist
		return (totalDist/ptCount)*(maxDist**2)  # average distance * max distance^2

	def _silhouette(self, partition: dict) -> float:
		"""
		partition: dictionary of centroids and assigned points.
		Returns average silhouette score for all points in partition.
		"""
		if partition is None:
			return -1
		partitionScore = 0
		centroids = [np.frombuffer(bufferCentroid) for bufferCentroid in partition.keys()]
		for bufferCentroid, points in partition.items():  # for each centroid
			if len(points) > 0: 
				centroidScore = 0
				parent = np.frombuffer(bufferCentroid)
				for pt in points:  # for each point in centroid
					second = self._findSecondCentroid(pt, parent, centroids)  # find closest centroid
					a = self._computeA(pt, partition[bufferCentroid])  # average dist of pt to other points in cluster
					b = self._computeB(pt, partition[second.tobytes()])  # average dist of pt to points in closest non parent cluster
					centroidScore += self._silhouetteCoeffient(a, b)  # (b-a)/max(a, b)
					
				partitionScore += centroidScore/len(points)
			else:  # has undesirable empty clusters
				return -1
		return partitionScore/len(centroids)

	def _silhouetteCoeffient(self, a: float, b: float) -> float:
		"""
		a: average dist of pt to other points in cluster.
		b: average dist of pt to points in closest non parent cluster.
		Returns silhouette coeffient for point given its a and b values.
		"""
		return (b-a)/max(a, b)

	def _computeA(self, pt: np.ndarray, points: np.ndarray) -> float:
		"""
		pt: point to compute "a" for.
		points: all points in cluster of pt.
		Returns avg dist from pt to all points.
		"""
		totalDist = 0
		size = len(points) - 1
		if size == 0:
			return 0
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _computeB(self, pt: np.ndarray, points: np.ndarray) -> float:
		"""
		pt: point to compute "b" for.
		points: all points in closest non parent cluster of pt.
		Returns avg dist from pt to all points.
		"""
		totalDist = 0
		size = len(points)
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _generateScores(self) -> None:
		"""
		Computes "matchness" scores for all points after clusters have been determined.
		Determines scores based on:
			1) Distance from pt to center of dataset (far away pts are penalized).
			2) Closeness of pt to center of its cluster relative to farthest pt from cluster (far pts are penalized).
			3) Avg dist of points from cluster (larger avg distances are penalized).
			4) Size of clusters (pts from smaller clusters are penalized).
		"""
		size = 0
		scores = np.zeros(self.data.shape[0])
		data =  np.zeros(self.data.shape)

		for centroid, points in self.items():
			clusterDistance = {
				"avg": 0,
				"total": 0,
				"max": 0,	
			}
			clusterSize = len(points)
			cache = {}

			# cache distance from pts to center of cluster
			for pt in points:
				distCentroidPt = Clusters.dist(centroid, pt)
				clusterDistance["total"] += distCentroidPt
				cache[pt.tobytes()] = distCentroidPt
				if distCentroidPt > clusterDistance["max"]:
					clusterDistance["max"] = distCentroidPt

			clusterDistance["avg"] = clusterDistance["total"]/clusterSize

			# compute scores for each pt
			for bufferPt, distCentroidPt in cache.items():
				pt = np.frombuffer(bufferPt)
				distFromCenter = Clusters.optimizedDist(pt, self._center)
				score = self._score(pt, distCentroidPt, clusterSize, clusterDistance["max"], clusterDistance["avg"], distFromCenter)
				scores[size] = score
				data[size] = pt
				size += 1

		# scale scores of pts from 0-100
		minScore, maxScore = scores.min(), scores.max()
		avgScore = scores.mean()
		scale = lambda pt: ((pt-minScore)/(maxScore-minScore))*100
		normalized = np.array(list(map(scale, scores)))
		
		# sorting
		order = normalized.argsort()
		self.orderedScores = normalized[order]
		self.orderedData = (data.T[:,order]).T

		# update public attributes
		self.rawScoreMin = minScore
		self.rawScoreMax = maxScore
		self.rawScoreAvg = avgScore
		self.scoreAvg = np.mean(normalized)

	def _score(self, pt: np.ndarray, distCentroidPt: float, clusterSize: int, clusterMax: float, avgClusterDist: float, distFromCenter: float) -> float:
		"""
		pt: pt to compute score for.
		distCentroidPt: dist between pt and center of cluster its in.
		clusterSize: num of pts in cluster of point.
		avgClusterDist: avg dist of points to center of cluster pt is a part of.
		distFromCenter: dist of pt from center of dataset.
		Computes score as described in "_generateScores". Uses exponents to weight terms.
		"""
		relativeClusterSize = (clusterSize/(self.data.shape[0]/self.k)) 
		relativeDist = (distCentroidPt/clusterMax)
		return (relativeClusterSize**2)*(np.sqrt(relativeDist**3))*avgClusterDist*(distFromCenter**2)

	def _simplify(self) -> None:
		"""
		Post: self values are simplified.
		Simplifies self by reducing values to their correct size.
		"""
		simplified = self._simpleCopy()
		self._revert(simplified)

	def _revert(self, copy: dict) -> None:
		"""
		Post: self values are simplified.
		Transforms values of self to values of copy.
		"""
		self.clear()
		for centroid, points in copy.items():
			self[centroid] = points

	def _kmeans(self, k: int) -> None:
		"""
		k: number of clusters.
		Computes k means clustering for values in self.data.
		"""
		if not k>0:
			raise ValueError("k must be greater than 0")

		self.clear()

		for _ in range(k):  # initialize centroids
			centroid = self._getRandomCentroid()
			self._add(centroid)

		for _ in range(self.maxIterations):  # train clusters until near convergence
			self._assign()
			self._update()
			if self._dp <= self._convergenceLimit*self._range:  # if centroids don't move very much
				self._assign()
				break

	def _getRandomCentroid(self) -> None:
		"""
		Returns coordinates with range of self._bounds (window of data)
		"""
		coords = np.zeros(self.data.shape[1])
		for dimension in range(self.data.shape[1]):
			coords[dimension] = Clusters.rand(self._bounds[dimension].min(), self._bounds[dimension].max())
		return coords

	def _findSecondCentroid(self, pt: np.ndarray, parent: np.ndarray, centroids: np.ndarray) -> np.ndarray:
		"""
		Returns centroid closest to pt other than centroid of cluster pt is in.
		"""
		closest, closestDist = None, 0
		initialized = False
		for centroid in centroids:
			if not np.all(centroid == parent):
				if not initialized:
					closest, closestDist = centroid, Clusters.optimizedDist(pt, centroid)
					initialized = True
				elif initialized:
					dist = Clusters.optimizedDist(pt, centroid)
					if dist <= closestDist:
						closest, closestDist = centroid, dist
		return closest

	def _add(self, centroid: np.ndarray) -> None:
		"""
		Post: coords of centroid added to self.
		Adds a centroid to self.
		"""
		self[centroid] = {"data": np.zeros((self.data.shape[0], self.data.shape[1])), "size": 0}

	def _assign(self) -> None:
		"""
		Post: values of centroid keys in self are filled.
		Assigns all points to centroid closest to them.
		"""
		if self._isAssigned:
			self._clearAssignments()
		else:
			self._isAssigned = True
		centroids = self.keys()
		for pt in self.data:
			closest, closestDist = centroids[0], Clusters.optimizedDist(pt, centroids[0])
			for centroid in centroids:
				dist = Clusters.optimizedDist(centroid, pt)
				if dist <= closestDist:
					closest, closestDist = centroid, dist
			self[closest]["data"][self[closest]["size"]] = pt
			self[closest]["size"] += 1

	def _update(self) -> None:
		"""
		Post: keys and their values are deleted and then updated keys are readded.
		Moves centroid closer to center of points assigned to it.
		"""
		maxDP = 0
		bufferCentroids = list(self._bufferKeys())
	
		for bufferCentroid in bufferCentroids:
			if self[bufferCentroid]["size"] > 0:
				centroid = np.frombuffer(bufferCentroid)

				data = self._getPoints(bufferCentroid)
				center = data.mean(axis=0)
				
				dp = self.alpha*(center-centroid)
				ds = self.dist(np.zeros(self.data.shape[1]), dp)

				if ds > maxDP:
					maxDP = ds

				del self[bufferCentroid]
				self._add(centroid+dp)
				
		self._dp = maxDP

	def _getPoints(self, centroid: np.ndarray or bytes) -> np.ndarray:
		"""
		centroid: centroid to get assigned pts from. Can be in np.ndarray or byte form.
		Returns points assigned to centroid.
		"""
		if not self._solved:
			return self[centroid]["data"][:self[centroid]["size"]]
		else:
			return self[centroid]

	def _simpleCopy(self) -> dict:
		"""
		Returns dict of centroid positions and points assigned to each centroid.
		"""
		copy = {}
		for centroid in self._bufferKeys():
			copy[centroid] = self._getPoints(centroid)
		return copy	

	def _clearAssignments(self) -> None:
		"""
		Post: values of self are cleared.
		Clears points assigned to each centroid.
		"""
		for centroid in self:
			self[centroid]["data"] = np.zeros((self.data.shape[0], self.data.shape[1]))
			self[centroid]["size"] = 0

	def _bufferKeys(self) -> type(dict().keys()):
		"""
		Returns dict_keys object of keys in form of bytes.
		"""
		return super().keys()

	def __setitem__(self, centroid: np.ndarray or bytes, points: np.ndarray) -> None:
		"""
		centroid: centroid to be used as key. Can be in np.ndarray or byte form.
		points: points to assign to centroid.
		Post: key's values are set.
		Sets value of key in self.
		"""
		if type(centroid) == np.ndarray:
			super().__setitem__(centroid.tobytes(), points)
		elif type(centroid) == bytes:
			super().__setitem__(centroid, points)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __getitem__(self, centroid: np.ndarray or bytes) -> np.ndarray:
		"""
		centroid: centroid to be used as key. Can be in np.ndarray or byte form.
		Returns item from key in self.
		"""
		if type(centroid) == np.ndarray:
			return super().__getitem__(centroid.tobytes())
		elif type(centroid) == bytes:
			return super().__getitem__(centroid)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __delitem__(self, centroid: np.ndarray or bytes) -> None:
		"""
		Post: Item is deleted from self.
		Deletes item from self.
		"""
		if type(centroid) == np.ndarray:
			return super().__delitem__(centroid.tobytes())
		elif type(centroid) == bytes:
			return super().__delitem__(centroid)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __iter__(self) -> iter(list()):
		"""
		Allows iteration through self.
		"""
		return [np.frombuffer(centroid) for centroid in self.keys()].__iter__()

