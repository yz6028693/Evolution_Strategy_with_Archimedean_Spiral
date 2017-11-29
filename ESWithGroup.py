import numpy as np
import matplotlib.pyplot as plt
from math import pi, sqrt
from shapely.geometry import Point
from operator import itemgetter


# Archimedean Spiral with Evolution Strategy
# The main goal of this small demo is to create points (red points) with Evolution Strategy algorithm
# to get close to every random points (blue points) created from Archimedean Spiral curve.

class ArchimedeanSpiralMeetES(object):
    def __init__(self):

        self.DNA_Elements = 3  # Number of elements each DNA has.
        self.DNA_Bound = [-6, 6]  # The bounds of DNA.
        self.Generations = 500  # Maximum generations in this program.
        self.Pop_Size = 100  # Number of population size.
        self.Kids_Size = 100  # Number of kids for each generation.

    # Function to transfer polar coordinate system to Cartesian coordinate system. （regular coordinate system）
    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return (x, -y)

    # Function to calculate the fitness (parameter we based on to define which individuals are better) of each individual (last and this generation).
    # The goal of our population (red points) is to get close to the blue points.
    # Since I think the blue points as different planets, I used the gravitation equation to calculate the fitness. Salute to Isaac Newton.
    def get_fitness(self, pop, XYList):
        Gravity = np.zeros([pop['DNA'].shape[0], 1])
        pop, XYList = self.UpdateXYList(pop, XYList)

        if len(XYList[0]) != 0:
            for i in range(pop['DNA'].shape[0]):
                for n in range(len(XYList[0])):
                    if pop['DNA'][i][2] != -1:

                        # Think the blue points as different planet, as a result, I choose to use the gravitation equation to differ the fitness, 6.674 is the gravitational constant.

                        Gravity[i] += 6.674 / ((pop['DNA'][i][0] - XYList[0][n]) ** 2 + (pop['DNA'][i][1] - XYList[1][n]) ** 2)
                    else:
                        Gravity[i] = 299792458  # The speed of light (Just a very big value.)
                        break
            return Gravity.flatten()
        else:
            return []


    # Keep good individuals based on the fitness we mentioned before.
    def keep_good_kids(self, pop, kids, XYList):
        oldpop = {}
        for key in ['DNA', 'Mutation']:
            oldpop[key] = pop[key]
            pop[key] = np.vstack((pop[key], kids[key]))
        fitness = self.get_fitness(pop, XYList)
        if len(fitness) != 0:
            idx = np.arange(pop['DNA'].shape[0])
            if idx[fitness.argsort()][- (len(oldpop['DNA']) + 1)] != 299792458:
                good_idx = idx[fitness.argsort()][-len(oldpop['DNA']):]
                for key in ['DNA', 'Mutation']:
                    pop[key] = pop[key][good_idx]
                return pop, 0
            else:
                return oldpop, 1
        else:
            return oldpop, 1


    # Remove occupied blue points from target points list
    def UpdateXYList(self, pop, XYList):
        deleteList = []
        for i in range(pop['DNA'].shape[0]):
            for m in range(len(XYList[0])):
                # If a red point is close enough to a blue point, we will not add the Gravity of this blue point to the fitness. (It will lose it attraction to red points)
                if sqrt(((pop['DNA'][i][0] - XYList[0][m]) ** 2 + (pop['DNA'][i][1] - XYList[1][m]) ** 2)) < 0.01:
                    pop['DNA'][i][2] = -1
                    if m not in deleteList:
                        deleteList.append(m)
        XYList[0] = np.delete(XYList[0], deleteList)
        XYList[1] = np.delete(XYList[1], deleteList)
        return pop, XYList


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


    # Function to create next generation (Based on the DNA and the mutation related to it.)
    # Note: Think DNA as the mean value of a normally distributed data and the mutation is its standard deviation.
    def make_kids(self, pop, Kids_Size, i):
        kids = {'DNA': np.zeros((Kids_Size, self.DNA_Elements)), 'Mutation': np.zeros((Kids_Size, self.DNA_Elements))}
        if i == 0 and Kids_Size != self.Pop_Size:
            for KidsDNA, KidsMutation in zip(kids['DNA'], kids['Mutation']):
                p1 = np.random.choice(np.arange(len(pop['DNA'])), size=1, replace=False)
                KidsDNA[0] = pop['DNA'][p1][0][0]
                KidsDNA[1] = pop['DNA'][p1][0][1]
                KidsMutation[0] = pop['Mutation'][p1][0][0]
                KidsMutation[1] = pop['Mutation'][p1][0][1]
                mutatexy = np.random.rand(*KidsMutation.shape) - 0.5
                KidsMutation[0] = np.maximum(KidsMutation[0] + mutatexy[0], 0.)
                KidsMutation[1] = np.maximum(KidsMutation[1] + mutatexy[1], 0.)
                KidsDNA[0] += KidsMutation[0] * np.random.randn(*KidsDNA[0].shape)
                KidsDNA[1] += KidsMutation[1] * np.random.randn(*KidsDNA[1].shape)
                KidsDNA[0] = np.clip(KidsDNA[0], *self.DNA_Bound)
                KidsDNA[1] = np.clip(KidsDNA[1], *self.DNA_Bound)
        else:
            for KidsDNA, KidsMutation in zip(kids['DNA'], kids['Mutation']):
                p1 = np.random.choice(np.arange(len(pop['DNA'])), size=2, replace=True)
                KidsDNA[0] = (pop['DNA'][p1[0]][0] + pop['DNA'][p1[1]][0])/2
                KidsDNA[1] = (pop['DNA'][p1[0]][1] + pop['DNA'][p1[1]][1])/2
                KidsMutation[0] = (pop['Mutation'][p1[0]][0] + pop['Mutation'][p1[1]][0])/2
                KidsMutation[1] = (pop['Mutation'][p1[0]][1] + pop['Mutation'][p1[1]][1])/2
                mutatexy = np.random.rand(*KidsMutation.shape) - 0.5
                KidsMutation[0] = np.maximum(KidsMutation[0] + mutatexy[0], 0.)
                KidsMutation[1] = np.maximum(KidsMutation[1] + mutatexy[1], 0.)
                KidsDNA[0] += KidsMutation[0] * np.random.randn(*KidsDNA[0].shape)
                KidsDNA[1] += KidsMutation[1] * np.random.randn(*KidsDNA[1].shape)
                KidsDNA[0] = np.clip(KidsDNA[0], *self.DNA_Bound)
                KidsDNA[1] = np.clip(KidsDNA[1], *self.DNA_Bound)
        return kids


    # Function for cluster analysis to separate points into different group
    def WithinArray(self, pop):
        row = []
        for i in range(len(pop['DNA'])):
            col = []
            if pop['DNA'][i][2] != -1:
                X_i = pop['DNA'][i][0]
                Y_i = pop['DNA'][i][1]
                for j in range(len(pop['DNA'])):

                    if pop['DNA'][j][2] != -1:
                        X_j = pop['DNA'][j][0]
                        Y_j = pop['DNA'][j][1]
                        if sqrt((X_j - X_i) ** 2  + (Y_j - Y_i) ** 2)  < 1.2:
                            within = 1
                        else:
                            within = 0
                    else:
                        within = 0
                    col.append(within)
            else:
                col = [0] * len(pop['DNA'])
            row.append(col)
        return np.array(row)


    # Separate Group for parallel work
    def GroupSeparator(self, pop):
        d_ij = self.WithinArray(pop)
        #densities = self.CalDensity(d_ij, cutoffdistance)
        temd_ij = d_ij
        Tribeclass = np.zeros(len(pop['DNA']))
        GroupNum = 0
        while True:
            if np.sum(temd_ij[np.argsort(np.sum(-temd_ij, axis=1))[0]]) < 5:
                break
            GroupNum += 1
            Tribeclass += GroupNum * temd_ij[np.argsort(np.sum(-temd_ij, axis=1))[0]]
            temd_ij = -(temd_ij[np.argsort(np.sum(-temd_ij, axis=1))[0]] - 1) * temd_ij
        for i in range(len(Tribeclass)):
            if pop['DNA'][i][2] != -1:
                pop['DNA'][i][2] =  Tribeclass[i]
        return pop


    def colors(self, array, ColorOptions):
        colorlist = []
        for i in range(len(array)):
            colorlist.append(ColorOptions[int(array[i])])
        return colorlist


    # Plot the process of this Evolution Strategy program.
    def plot(self):
        pop = dict(DNA=5 * np.random.rand(1, self.DNA_Elements).repeat(self.Pop_Size, axis=0),
                   Mutation=np.random.rand(self.Pop_Size, self.DNA_Elements))
        pop['DNA'][:, 2] = 0
        pop['Mutation'][:, 2] = 0
        plt.ion()
        plt.figure(figsize=(9, 7))
        plt.rcParams['axes.facecolor'] = (0.2, 0.2, 0.2)
        XYList = self.RandomPoints(20)
        XYList1 = self.PlotArchimedeanSpiral()
        bg1 = plt.plot(XYList1[0], XYList1[1], 'w--')
        bg2 = plt.scatter(XYList[0], XYList[1], s=30, c='b', edgecolors='white', linewidth='0.5', zorder=10)
        sca = []
        for _ in range(self.Generations):
            newpop = dict(DNA=np.array([]), Mutation=np.array([]))
            if len(np.where(pop['DNA'][:, 2] == -1)[0]) != 0:
                FinishedList = dict(DNA=np.array([]), Mutation=np.array([]))
                for key in ['DNA', 'Mutation']:
                    FinishedList[key] = pop[key][np.where(pop['DNA'][:, 2] == -1)]
            else:
                FinishedList = np.array([])
            for i in np.unique(pop['DNA'][:, 2]):
                if i != -1:
                    GroupPop = dict(DNA=np.array([]), Mutation=np.array([]))
                    for key in ['DNA', 'Mutation']:
                        GroupPop[key] = pop[key][np.where(pop['DNA'][:, 2] == i)]
                    GroupPopSize = len(np.where(pop['DNA'][:, 2] == i)[0])
                    GroupKids = self.make_kids(GroupPop, GroupPopSize, i)
                    GroupPop, trigger = self.keep_good_kids(GroupPop, GroupKids, XYList)
                    if trigger == 1:
                        break
                    for key in ['DNA', 'Mutation']:
                        if len(newpop[key]) == 0:
                            newpop[key] = GroupPop[key]
                        else:
                            newpop[key] = np.append(newpop[key], GroupPop[key], axis=0)
            if trigger == 1:
                print('Finished!')
                print('Number of generations: ', _)
                break

            pop = self.GroupSeparator(newpop)
            try:
                for key in ['DNA', 'Mutation']:
                    pop[key] = np.append(newpop[key], FinishedList[key], axis=0)
            except:
                pass

            colors = ['b', 'c', 'y', 'g', 'm', 'w', 'k', 'r']
            labels = ['Outliers', 'Group1', 'Group2', 'Group3', 'Group4', 'Group5', 'Group6', 'Group7', 'Group8',
                      'Group9', 'Occupied']
            if sca:
                for m in range(len(sca)):
                    sca[m].remove()
                sca = []
            for i in np.unique(pop['DNA'][:, 2]):
                sca.append(plt.scatter(pop['DNA'][np.where(pop['DNA'][:, 2] == i)][:, 0], pop['DNA'][np.where(pop['DNA'][:, 2] == i)][:, 1], s=100, lw=0, c=self.colors(pop['DNA'][np.where(pop['DNA'][:, 2] == i)][:, 2], colors), alpha=0.9, label=labels[int(i)]))
            plt.legend(loc='upper left', numpoints=1, ncol=1, fontsize=10, bbox_to_anchor=(1, 1));plt.pause(0.02)
            plt.margins(0.1)
            plt.subplots_adjust(right = 0.8)
        plt.ioff();plt.show()


if __name__ == '__main__':
    tool = ArchimedeanSpiralMeetES()
    tool.plot()
