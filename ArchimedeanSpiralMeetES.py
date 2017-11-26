import numpy as np
import matplotlib.pyplot as plt
from math import pi, sqrt

# Archimedean Spiral with Evolution Strategy
# The main goal of this small demo is to create points (red points) with Evolution Strategy algorithm
# to get close to every random points (blue points) created from Archimedean Spiral curve.

class ArchimedeanSpiralMeetES(object):

    def __init__(self):

        self.DNA_Elements = 3            # Number of elements each DNA has.
        self.DNA_Bound = [-6, 6]         # The bounds of DNA.
        self.Generations = 500           # Maximum generations in this program.
        self.Pop_Size = 100              # Number of population size.
        self.Kids_Size = 50              # Number of kids for each generation. Note: in this demo we used the asexual reproduction which each individual in last generation can create kids by itself.


    # Function to transfer polar coordinate system to Cartesian coordinate system. （regular coordinate system）
    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return (x, -y)

    # Function to calculate the fitness (parameter we based on to define which individuals are better) of each individual (last and this generation).
    # The goal of our population (red points) is to get close to the blue points.
    # Since I think the blue points as different planets, I used the gravitation equation to calculate the fitness. Salute to Isaac Newton.
    def get_fitness(self, pred, XYList):
        Gravity = np.zeros([pred.shape[0], 1])
        XList = XYList[0]
        YList = XYList[1]

        deleteList = []
        for i in range(pred.shape[0]):
            for m in range(len(XYList[0])):
                
                # If a red point is close enough to a blue point, we will not add the Gravity of this blue point to the fitness. (It will lose it attraction to red points)
                
                if sqrt(((pred[i][0] - XYList[0][m]) ** 2 + (pred[i][1] - XYList[1][m]) ** 2)) < 0.01:  
                    pred[i][2] = 1
                    deleteList.append(m)


        XList = np.delete(XList, deleteList)
        YList = np.delete(YList, deleteList)
        XYList[0] = XList
        XYList[1] = YList

        if len(XList) != 0:
            for i in range(pred.shape[0]):
                for n in range(len(XList)):
                    if pred[i][2] != 1:
                        
                        # Think the blue points as different planet, as a result, I choose to use the gravitation equation to differ the fitness, 6.674 is the gravitational constant.
                        
                        Gravity[i] += 6.674 / ((pred[i][0] - XList[n]) ** 2 + (pred[i][1] - YList[n]) ** 2)  
                    else:
                        Gravity[i] = 299792458   # The speed of light (Just a very big value.)
                        break
            return Gravity.flatten()
        else:
            return []

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
        return [x_1, y_1, x_2, y_2]

    # Function to create data for ploting Archimedean Spiral curve.
    def PlotArchimedeanSpiral(self):
        phi = [2 * i * (2 * pi / 360) for i in range(270)]
        rho1 = np.multiply(phi, 0.5)
        x_1, y_1 = self.pol2cart(rho1, phi)
        return [x_1, y_1]

    # Function to create next generation (Based on the DNA and the mutation related to it.)
    # Note: Think DNA as the mean value of a normally distributed data and the mutation is its standard deviation.
    def make_kids(self, pop, Kids_Size):
        kids = {'DNA': np.zeros((Kids_Size, self.DNA_Elements)), 'Mutation': np.zeros((Kids_Size, self.DNA_Elements))}
        for KidsDNA, KidsMutation in zip(kids['DNA'], kids['Mutation']):
            while True:
                p1 = np.random.choice(np.arange(self.Pop_Size), size=1, replace=False)
                if pop['DNA'][p1][0][2] != 1:
                    break
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
        return kids


    # Keep good individuals based on the fitness we mentioned before.
    def keep_good_kids(self, pop, kids, XYList):
        oldpop = {}
        for key in ['DNA', 'Mutation']:
            oldpop[key] = pop[key]
            pop[key] = np.vstack((pop[key], kids[key]))

        fitness = self.get_fitness(pop['DNA'], XYList)
        if len(fitness) != 0:
            idx = np.arange(pop['DNA'].shape[0])
            if idx[fitness.argsort()][- (self.Pop_Size+1)] != 299792458:
                good_idx = idx[fitness.argsort()][-self.Pop_Size:]
                for key in ['DNA', 'Mutation']:
                    pop[key] = pop[key][good_idx]
                return pop, 0
            else:
                return oldpop, 1
        else:
            return oldpop, 1


    # Plot the process of this Evolution Strategy program.
    def plot(self):
        global sca
        pop = dict(DNA=5 * np.random.rand(1, self.DNA_Elements).repeat(self.Pop_Size, axis=0),
                   Mutation=np.random.rand(self.Pop_Size, self.DNA_Elements))
        pop['DNA'][:, 2] = 0
        pop['Mutation'][:, 2] = 0

        plt.ion()
        plt.rcParams['axes.facecolor'] = (0.2, 0.2, 0.2)
        XYList = self.RandomPoints(20)
        XYList1 = self.PlotArchimedeanSpiral()
        bg1 = plt.plot(XYList1[0], XYList1[1], 'w--')
        bg2 = plt.scatter(XYList[0], XYList[1], s=30, c='b', edgecolors='white', linewidth='0.5', zorder=10)
        for _ in range(self.Generations):
            if 'sca' in globals(): sca.remove()
            sca = plt.scatter(pop['DNA'][:, 0], pop['DNA'][:, 1], s=100, lw=0, c='red', alpha=0.8); plt.pause(0.05)
            kids = self.make_kids(pop, self.Kids_Size)
            pop, trigger = self.keep_good_kids(pop, kids, XYList)
            if trigger == 1:
                print('Finished!')
                print('Number of generations: ', _)
                break
        plt.ioff(); plt.show()

if __name__ == '__main__':
    tool = ArchimedeanSpiralMeetES()
    tool.plot()
