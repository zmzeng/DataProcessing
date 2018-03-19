# -*- coding: utf-8 -*-

import re
import sys
import matplotlib.pyplot as plt

class xpsProcess(object):
    """
    Description: 
        This script read in .txt file generated by X-ray photoelectron spectroscopy
        and revise all data according to the standard energy of Carbon (default is 284.6eV).
        Finally all data after revising will be will be plot and 
        output in .txt file named with the atom types.

    Usage: 
            $ python xpsProcess.py <file2Process> [standardEnergyOfCarbon]

    Args:
        file2Process (str): path to .txt file, define which file to process.
        standardEnergyOfCarbon (float, optional): standard energy of Carbon for revise. default is 284.6eV.

    Attributes:
        self.file2Process (str): path to .txt file, define which file to process.
        self.standardEnergyOfCarbon (float): standard energy of Carbon for revise.
        self.atoms (str): atom type found in the .txt file.
        self.spectrum (list): list of spectrum for each atom.
        self.delta (float)：difference between experiment and standard energy of Carbon.

    Output: 
        Figure for each atom spectrum and save in .png files.
        Several .txt files named with the concerned atom types, in which contains the revaised energy, 
        counts and the original energy. 


    code by zmzeng12 20180314
    """

    def __init__(self, py, file2Process, standardEnergyOfCarbon=284.6):

        welcome = '''
#######################################################

  X-ray photoelectron spectroscopy data process script  
                    code by zmzeng.
                       20180314

#######################################################
    '''
        print(welcome)
        self.file2Process = file2Process
        self.standardEnergyOfCarbon = float(standardEnergyOfCarbon)

        print('------>  ' + 'The file to process is ' + self.file2Process)
        print('------>  ' + 'The standard energy of C is set to ' + str(self.standardEnergyOfCarbon) +'\n')
        self.atoms = []
        self.spectrum = []
        self.delta = 0.0

    def readFile(self):
        file = open(self.file2Process, 'r')
        line = file.readline()
        while line:
            # every atom data is start with line with 'Region'
            if line.find('Region') != -1:
                line = self.getData(file)
            else:
                break
        file.close()
        print('------>  ' + 'Found atoms: '+ str(self.atoms[1:]) +'\n')

    def getData(self, file):
        line = file.readline()
        # use RegExr to match the atom type
        atom = re.search('false\s(.*?)\s7', line).group(1)
        self.atoms.append(atom)
        line = file.readline()
        line = file.readline()
        line = file.readline()
        line = file.readline()
        energyData = []
        countsData = []
        # all atom experiment data are stored in self.spectrum
        while line.find('Region') == -1 and line:
            if line.find('Layer') != -1 :
                line = file.readline()
                line = file.readline()
                line = file.readline()
            data = [float(x) for x in line.split('\t')]
            energyData.append(data[0])
            countsData.append(data[1])
            line = file.readline()
        self.spectrum.append([energyData, countsData])
        return line
   
    def findDelta(self):
        """Find the energy of Carbon from experiment data. Compare the experiment value and the standard value
        to get the Delta for later data revising.

        Delta = Esignal - Estandard
        """
        energyData = self.spectrum[self.atoms.index('C')][0]
        countsData = self.spectrum[self.atoms.index('C')][1]
        indexOfMaxCounts = 0
        maxCounts = 0
        for i in range(0,len(countsData)):
            if maxCounts < countsData[i]:
                maxCounts = countsData[i]
                index = i
            i += 1
        energyOfCarbon = energyData[indexOfMaxCounts]
        self.delta = energyOfCarbon - self.standardEnergyOfCarbon
        print('------>  ' + 'max position is ' + str(energyOfCarbon))
        print('------>  ' + 'delta is ' + str(self.delta) + '\n')

    def reviseData(self, energyData):
        """Revise data according to Delta.

        Estandard = Esignal - Delta"""
        # return str(data[0]-self.delta) + '  ' + str(data[1]) + '  ' + str(data[0])
        return [i-self.delta for i in energyData]

    def outputData(self):
        for i in range(0,len(self.atoms)):
            if self.atoms[i] == '':
                self.atoms[i] = 'whole spectrum'
            file = open(self.file2Process[0:-4] + '_' + self.atoms[i] + '_Result.txt', 'w')
            file.write(self.atoms[i] + ' generated by xpsProcess.exe\n')
            file.write('Energy(revised)  Counts  Energy\n')
            file.write('eV none eV \n')
            file.write(self.atoms[i] + ' ' + self.atoms[i] + ' ' + self.atoms[i] + '\n')
            for energyRevised, counts, energy in zip(self.reviseData(self.spectrum[i][0]), self.spectrum[i][1], self.spectrum[i][0]):
                file.write('%.2f  %s  %.2f \n' %(energyRevised, counts, energy))
            file.close()

    def plotData(self):
        for i in range(0, len(self.atoms)):
            if self.atoms[i] == 'C' or self.atoms[i] == 'O':
                continue
            plt.figure('XPS spectrum: ' + self.atoms[i])
            plt.plot(self.reviseData(self.spectrum[i][0]), self.spectrum[i][1])
            plt.xlabel('Energe (eV)')
            plt.ylabel('Counts')
            plt.title('XPS spectrum: ' + self.atoms[i])
            plt.gca().invert_xaxis() 
        plt.show()

    def main(self):

        self.readFile()
        self.findDelta()
        self.plotData()
        self.outputData()

if __name__=='__main__':

    
    try:
        test = xpsProcess(*sys.argv)
    except TypeError:
        print("Something wrong with your input.\n ")
        print(xpsProcess.__doc__)
        input('press Enter to quit.\n\n')
    else:
        try:
            test.main()
        except FileNotFoundError:
            print("Something wrong with your data file, Check filename.")
            print(xpsProcess.__doc__)
            input('Press Enter to quit.\n\n')
        except TypeError:
            print("Something wrong with the standard energy value of Carbon.")
            print(xpsProcess.__doc__)
            input('Press Enter to quit.\n\n')
        else:
            print('                    ###############')
            print('                    #  all done!  #' )
            print('                    ###############\n')
            print('Press Enter to quit.\n')
            standardEnergyOfCarbon = input('Or \n\nInput the standard energy of Carbon if it is *NOT* 284.6\n')
            if standardEnergyOfCarbon:
                print('\n')
                test = xpsProcess(*sys.argv, standardEnergyOfCarbon)
                test.main()


