import numpy as np
import matplotlib.pyplot as plt
from math import pi, sqrt
from operator import itemgetter
import time

class ClusteringWithDensity(object):


    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return (x, -y)

    def RandomArchimedeanSpiralPoints(self):
        phi = [2 * i * (2 * pi / 360) for i in range(270)]
        rho1 = np.multiply(phi, 0.5)
        x1, y1 = self.pol2cart(rho1, phi)
        return [x1, y1]

    def RandomPoints(self, i):
        x1, y1 = np.random.multivariate_normal([-i, 0], [[1, 0], [0, 1]], int(500)).T
        x2, y2 = np.random.multivariate_normal([i, 0], [[1, 0], [0, 1]], int(500)).T
        x = np.hstack((x1, x2))
        y = np.hstack((y1, y2))
        points = np.vstack([x, y])
        return points

    def CalDistanceAndDensity(self, Array, cutoffdistance):
        Distance = []
        Density = []
        withinArray = []
        for i in range(len(Array[0])):
            within = 0
            col = []
            col1 = []
            X_i = Array[0][i]
            Y_i = Array[1][i]
            for j in range(len(Array[0])):
                X_j = Array[0][j]
                Y_j = Array[1][j]
                distance = sqrt((X_i - X_j) ** 2 + (Y_i - Y_j) ** 2)
                col.append(distance)
                if distance < cutoffdistance:
                    col1.append(1)
                    within += 1
                else:
                    col1.append(0)
            Distance.append(col)
            withinArray.append(col1)
            Density.append(within)
        return np.array(Distance), np.array(Density), np.array(withinArray)

    def NearestDistanceWithHigherDensity(self, distance_ij, Density):
        NearestDistanceWithHigherDensity = []
        NearNeighborWithHigherDensity = []
        for i in range(len(Density)):
            if Density[i] != np.amax(Density):
                HigherDensityIDForI = np.where(Density > Density[i])
                NearestDistanceForI = np.amin(distance_ij[i][HigherDensityIDForI])
                NearNeighborForI = np.where(distance_ij[i] == NearestDistanceForI)
            else:
                NearestDistanceForI = np.amax(distance_ij[i])
                NearNeighborForI = np.array([i], dtype='int')
            NearestDistanceWithHigherDensity.append(NearestDistanceForI)
            NearNeighborWithHigherDensity.append(NearNeighborForI)
        return np.array(NearestDistanceWithHigherDensity), np.array(NearNeighborWithHigherDensity)

    def ClusterCenter(self, Density, NearestDistanceArray):
        ClusterCenters = []
        for i in range(len(Density)):
            # The Rule is flexible, here my rule is to find the cluster centers with density higher than 10 percents
            # of all points and nearest distances higher than 2 times of average nearest distances
            if Density[i] > Density[np.argsort(Density)][round(len(Density) * 0.3)] and \
                            NearestDistanceArray[i] > 2.5 * np.average(NearestDistanceArray):
                ClusterCenters.append([i, Density[i]])
        ClusterCenters.sort(key=itemgetter(1))
        return np.array(ClusterCenters)

    def ReverseSearch(self, NearNeighborArray, Core, center):
        FinalHalos = np.array([], dtype='int')
        halos = []
        halos.append(Core[0])
        while True:
            halo = np.array([], dtype='int')
            for ID in halos[-1]:
                halo = np.append(halo, np.where(NearNeighborArray == ID)[0])
                NearNeighborArray[np.where(NearNeighborArray == ID)] = -1
            if len(halo) == 0:
                break
            halos.append(halo)
        for haloI in halos:
            FinalHalos = np.append(FinalHalos, haloI)
        FinalHalos = np.unique(FinalHalos)
        return FinalHalos

    def AssignOtherPoints(self, ClusterCenters, NearNeighborArray, withinArray):
        Clusters = np.zeros(len(NearNeighborArray))
        for i in ClusterCenters[:, 0]:
            ClusterNum = len(np.unique(Clusters))
            core = np.where(withinArray[i] == 1)
            cluster = self.ReverseSearch(NearNeighborArray, core, i)
            for n in cluster:
                if n in np.where(Clusters == 0)[0]:
                    Clusters[n] = ClusterNum
        return Clusters

    def colors(self, array, ColorOptions):
        colorlist = []
        for i in range(len(array)):
            colorlist.append(ColorOptions[int(array[i])])
        return colorlist


    def Clustering(self):
        global sca
        colors = ['black', 'c', 'y', 'g', 'm', 'r', 'b']
        plt.figure(figsize=(9, 7))
        for i in range(6,-6,-1):
            ArchimedeanSpiralPoints = self.RandomPoints(i)
            distance_ij, Density, withinArray  = self.CalDistanceAndDensity(ArchimedeanSpiralPoints, 1)
            NearestDistanceArray, NearNeighborArray = self.NearestDistanceWithHigherDensity(distance_ij, Density)
            ClusterCenters = self.ClusterCenter(Density, NearestDistanceArray)
            Clusters = self.AssignOtherPoints(ClusterCenters, NearNeighborArray, withinArray)
            if 'sca' in globals(): sca.remove()
            sca = plt.scatter(ArchimedeanSpiralPoints[0,:], ArchimedeanSpiralPoints[1,:], s=100, lw=0, c=self.colors(Clusters, colors), alpha=0.9);
            plt.pause(0.02)
        plt.ioff();plt.show()




if __name__ == '__main__':
    print("Start time:" + str(time.asctime(time.localtime(time.time()))))
    tool = ClusteringWithDensity()
    tool.Clustering()
    print("End time:" + str(time.asctime(time.localtime(time.time()))))