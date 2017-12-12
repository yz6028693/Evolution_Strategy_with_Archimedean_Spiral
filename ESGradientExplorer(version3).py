import numpy as np
import matplotlib.pyplot as plt
from math import pi, sqrt
from shapely.geometry import Point
from operator import itemgetter
import multiprocessing as mp


# Archimedean Spiral with Evolution Strategy
# The main goal of this small demo is to create points (red points) with Evolution Strategy algorithm
# to get close to every random points (blue points) created from Archimedean Spiral curve.

class ESGradientExplorer(object):

    def __init__(self):

        self.DNA_Elements = 3  # Number of elements each DNA has.
        self.DNA_Bound = [-6, 6]  # The bounds of DNA.
        self.Generations = 500  # Maximum generations in this program.
        self.Pop_Size = 100  # Number of population size.
        self.Kids_Size = 100  # Number of kids for each generation.
        self.sigma = 0.05
        self.alpha = 0.008

    # Function to transfer polar coordinate system to Cartesian coordinate system. （regular coordinate system）
    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return (x, -y)


    def InitPoint(self, nums):
        InitPoint = 6 * np.random.rand(nums, 2)
        return InitPoint


    def KidsWithNoise(self, CenterPoint, sigma):
        CenterPoint = np.expand_dims(CenterPoint, 0)
        noise =  np.random.randn(self.Pop_Size, 2)
        kidswithnoise = CenterPoint.repeat(self.Pop_Size, axis=0) + sigma * noise
        return kidswithnoise, noise


    # Function to calculate the fitness (parameter we based on to define which individuals are better) of each individual (last and this generation).
    # The goal of our population (red points) is to get close to the blue points.
    # Since I think the blue points as different planets, I used the gravitation equation to calculate the fitness. Salute to Isaac Newton.
    def get_rewards(self, kidswithnoise, XYList):

        Gravity = np.zeros(self.Pop_Size)

        for n in range(len(XYList[0])):
            # Think the blue points as different planet, as a result, I choose to use the gravitation equation to differ the fitness, 6.674 is the gravitational constant.
            Gravity += 6.674 / (
            (kidswithnoise[:, 0] - XYList[0][n]) ** 2 + (kidswithnoise[:, 1] - XYList[1][n]) ** 2)

        NormalizedGravity = (Gravity - np.mean(Gravity)) / np.std(Gravity)

        return NormalizedGravity


    def UpdateCenterPoint(self, CenterPoint, NormalizedRewards, noise, alpha, sigma):

        updatedCenterPoint = CenterPoint + alpha/(self.Pop_Size * sigma) * np.dot(noise.T, NormalizedRewards)

        return updatedCenterPoint

    def ArrayCheckExist(self, CenterPoint, FinishedList):
        for item in FinishedList:
            if CenterPoint.all == item.all:
                return False
        return True


    # Remove occupied blue points from target points list
    def UpdateXYList(self, CenterPoints, XYList, FinishedList):
        deleteI = []
        for i in range(len(XYList[0])):
            for CenterPoint in CenterPoints:
                # If a red point is close enough to a blue point, we will not add the Gravity of this blue point to the fitness. (It will lose it attraction to red points)
                if sqrt(((CenterPoint[0] - XYList[0][i]) ** 2 + (CenterPoint[1] - XYList[1][i]) ** 2)) < 0.01:
                    if self.ArrayCheckExist(CenterPoint, FinishedList):
                        FinishedList.append(CenterPoint)
                    if i not in deleteI:
                        deleteI.append(i)
                    break
        if len(deleteI) != 0:
            XYList[0] = np.delete(XYList[0], deleteI)
            XYList[1] = np.delete(XYList[1], deleteI)
        return FinishedList, XYList


    def WorkFlow(self, CenterPoint, XYList, sigma, alpha):
        kidswithnoise, noise = self.KidsWithNoise(CenterPoint, sigma)
        NormalizedRewards = self.get_rewards(kidswithnoise, XYList)
        updatedCenterPoint = self.UpdateCenterPoint(CenterPoint, NormalizedRewards, noise, alpha, sigma)
        #updatedCenterPoint, kidswithnoise = self.WorkFlow(CenterPoint, XYList)

        return updatedCenterPoint, kidswithnoise


    def plot(self, N_workers):
        global scaf
        FinishedList = []
        plt.figure(figsize=(9, 7))
        plt.rcParams['axes.facecolor'] = (0.2, 0.2, 0.2)
        plt.margins(0.1)
        plt.subplots_adjust(right=0.8)
        sca = []

        pool = mp.Pool(N_workers)
        XYList = self.RandomPoints(20)
        XYList1 = self.PlotArchimedeanSpiral()
        bg1 = plt.plot(XYList1[0], XYList1[1], 'w--')
        bg2 = plt.scatter(XYList[0], XYList[1], s=30, c='b', edgecolors='white', linewidth='0.5', zorder=10)
        sigmas = np.random.uniform(low=0.03, high=0.06, size=(N_workers))
        alphas = np.random.uniform(low=0.008, high=0.011, size=(N_workers))
        InitPoints = self.InitPoint(N_workers)
        CenterPoints = InitPoints
        colors = ['c', 'y', 'g', 'm', 'w', 'k', 'r']
        labels = ['Explorer1', 'Explorer2', 'Explorer3', 'Explorer4', 'Explorer5', 'Explorer6', 'Explorer7', 'Explorer8',
                  'Explorer9']

        while len(XYList[0]) != 0:

            if sca:
                for m in range(len(sca)):
                    sca[m].remove()
                sca = []
            if 'scaf' in globals(): scaf.remove()

            #updatedCenterPoint, sca = self.WorkFlow(CenterPoint, XYList)


            explorers = [pool.apply_async(self.WorkFlow, (CenterPoints[i], XYList, sigmas[i], alphas[i]))
                         for i in range(N_workers)]

            PoolReturns = [returns.get() for returns in explorers]
            updatedCenterPoints = [explorer[0] for explorer in PoolReturns]
            Differentkidswithnoise = [explorer[1] for explorer in PoolReturns]

            i = 0

            for kidswithnoise in Differentkidswithnoise:
                sca.append(plt.scatter(kidswithnoise[:, 0], kidswithnoise[:, 1], s=100,
                                       c=colors[i], alpha=0.9))
                i += 1

            i = 0
            for CenterPoint in CenterPoints:
                sca.append(plt.scatter(CenterPoint[0], CenterPoint[1], s=100, edgecolors='w',
                                   linewidth='1.0', c=colors[i], alpha=1.0, label=labels[i]))
                i += 1

            CenterPoints = np.vstack([updatedCenterPoint for updatedCenterPoint in updatedCenterPoints])
            FinishedList, XYList = self.UpdateXYList(CenterPoints, XYList, FinishedList)

            if len(FinishedList) != 0:
                ArrayFinishedList = np.array(FinishedList)
                scaf = plt.scatter(ArrayFinishedList[:, 0], ArrayFinishedList[:, 1], s=100, lw=0,
                                   c='red', alpha=0.9, label='Occupied')
            plt.legend(loc='upper left', numpoints=1, ncol=1, fontsize=10, bbox_to_anchor=(1, 1)); plt.pause(0.02)
        print('Finished!')

        plt.ioff(); plt.show()


    # Function to create random points from Archimedean Spiral curve.
    def RandomPoints(self, num):
        phi1inx = np.random.choice(np.arange(540), size=num, replace=False)
        phi2inx = np.random.choice(np.arange(540), size=num, replace=False)
        phi1 = [i * (2 * pi / 360) for i in phi1inx]
        phi2 = [i * (2 * pi / 360) for i in phi2inx]
        rho1 = np.multiply(phi1, 0.5)
        rho2 = np.multiply(phi2, -0.5)
        x_1, y_1 = self.pol2cart(rho1, phi1)
        x_2, y_2 = self.pol2cart(rho2, phi2)
        return [x_1, y_1]


    # Function to create data for ploting Archimedean Spiral curve.
    def PlotArchimedeanSpiral(self):
        phi = [2 * i * (2 * pi / 360) for i in range(270)]
        rho1 = np.multiply(phi, 0.5)
        x_1, y_1 = self.pol2cart(rho1, phi)
        return [x_1, y_1]


    def colors(self, array, ColorOptions):
        colorlist = []
        for i in range(len(array)):
            colorlist.append(ColorOptions[int(array[i])])
        return colorlist


if __name__ == '__main__':
    tool = ESGradientExplorer()
    tool.plot(3)