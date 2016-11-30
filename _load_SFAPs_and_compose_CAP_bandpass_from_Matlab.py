import cPickle as pickle
import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.cm as cm
import matplotlib.colors as colors

saveDict = pickle.load(open(os.path.join('/media/carl/4ECC-1C44/PyPN/SFAPs', 'SFAPsPowleyMyelAsRecordings.dict'), "rb" )) # thinnerMyelDiam # SFAPsPowleyMyelAsRecordingsNewCurr


# saveDict = {'unmyelinatedDiameters' : diametersUnmyel,
#             'unmyelinatedSFAPsHomo': [],
#             'unmyelinatedSFAPsFEM': [],
#             'unmyelinatedCV' : [],
#             't': [],
#             'myelinatedDiameters': diametersMyel,
#             'myelinatedSFAPsHomo': [],
#             'myelinatedSFAPsFEM': [],
#             'myelinatedCV' : [],
#             }

from scipy.signal import butter, lfilter, freqz

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# parameters
lengthOfRecording = 200 #ms
dt = 0.0025 #ms
nRecording = lengthOfRecording/dt
tArtefact = 0.1 # ms
nArtefact = tArtefact/dt

electrodeDistance = 70. # mm
jitterAmp = 5 #ms
jitterDist = 0.03*electrodeDistance #
numMyel = 10
numUnmyel = 10
poles = 2
poleDistance = 1 # mm
polePolarities = [1, -1]
fieldTypes = [0, 1] # 0: homo, 1: FEM

timePlotMin = 10
timePlotMax = 35

stringsDiam = ['unmyelinatedDiameters', 'myelinatedDiameters']
stringsSFAPHomo = ['unmyelinatedSFAPsHomo', 'myelinatedSFAPsHomo']
stringsSFAPFEM = ['unmyelinatedSFAPsFEM', 'myelinatedSFAPsFEM']
stringsCV = ['unmyelinatedCV', 'myelinatedCV']
# tUnmyel = saveDict['unmyelinatedT']
# tMyel = saveDict['myelinatedT']
# ts = [tUnmyel, tMyel]
tHomo = saveDict['t']
ts = [tHomo, np.arange(0,10,0.0025)]

wantedNumbersOfFibers = [(0.0691040631732923, 0.182192465406599, 0.429980837522710, 0.632957475186409, 2.05015339910575,
                          3.10696898591111,  4.54590886074274,  7.22064649366380,  7.60343269800399,  8.61543655035694,
                          8.07683524571988,  7.15617584468796,  7.04457675416097,  6.77590492234067,  5.67583310442061,
                          5.20464797635635,  3.22856301277829,  2.51011904564906,  2.06140597644239,  1.50026642131635,
                          1.32118496258518,  0.849999834520921, 0.760773515404445, 0.312027350382088, 0.200593738933586,
                          0.201222559431810, 0.15, 0.1),
                         (0.6553, 0.658, 2.245, 2.282, 4.627, 4.665, 16.734, 16.737, 19.393, 19.396, 17.776, 17.779,
                          15.503, 15.506, 9.26, 9.234, 5.993, 5.961, 2.272, 2.275, 2.138, 2.106, 1.734, 1.634, 1.151,
                          1.189, 0.948, 0.917, 2.1, 2.1)]

diametersMyel = np.array(saveDict[stringsDiam[1]])
sigma = 0.25
mu = .7
wantedNumbersOfFibers[1] = 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (diametersMyel - mu)**2 / (2 * sigma**2) )

wantedNumbersOfFibers[0] = np.divide(wantedNumbersOfFibers[0],  np.sum(wantedNumbersOfFibers[0]))*numUnmyel
wantedNumbersOfFibers[1] = np.divide(wantedNumbersOfFibers[1],  np.sum(wantedNumbersOfFibers[0]))*numMyel

# -------------------- plot recorded data ---------------------------------
import testWaveletDenoising as w
data = np.loadtxt('/media/carl/18D40D77D40D5900/Dropbox/_Exchange/Project/SD_1ms_AllCurrents.txt')
denoisedVoltage = w.wden(data[:,1], level=12, threshold=1.5)

tStart = 3.0245 # 3.024 #
time = data[:,0]
tCut = (time[time>tStart] - tStart)*1000
vDenCut = denoisedVoltage[time>tStart]

# plt.plot(tCut, vDenCut/np.max(vDenCut), color='red', label='Experimental data')
# plt.show()

plt.plot(tCut[np.logical_and(tCut>timePlotMin, tCut<timePlotMax)], vDenCut[np.logical_and(tCut>timePlotMin, tCut<timePlotMax)]/np.max(vDenCut[np.logical_and(tCut>timePlotMin, tCut<timePlotMax)]), color='black', linewidth=2, label='Experimental data')
# plt.show()

tCAP = np.arange(0,lengthOfRecording,0.0025)

fieldStrings = ['Homogeneous', 'FEM']
for fieldTypeInd in [0]: # fieldTypes:
    CAP = np.zeros(nRecording)

    for typeInd in [1]:

        diameters = np.array(saveDict[stringsDiam[typeInd]])
        CVs = np.array(saveDict[stringsCV[typeInd]])
        t = ts[typeInd]
        numFibers = len(diameters)

        # wanted number of fibers per diameter
        # wantedNums = np.ones(numFibers)*1000
        wantedNums = wantedNumbersOfFibers[typeInd]

        if fieldTypeInd == 0:
            SFAP = np.transpose(np.array(saveDict[stringsSFAPHomo[typeInd]]))
        else:
            SFAP = np.transpose(np.array(saveDict[stringsSFAPFEM[typeInd]]))

        SFAPNoArt = SFAP [t > tArtefact, :]

        for fiberInd in range(numFibers):

            currentSFAP = SFAPNoArt[:, fiberInd]

            # first find maximum position in signal
            peakInd = np.argmax(currentSFAP)

            # plt.plot(diameters, CVs)
            # plt.show()
            if typeInd == 1:
                CV = CVs[fiberInd]
            else:
                CV = np.sqrt(diameters[fiberInd]) * 2

            # print 'diameter : ' + str(diameters[fiberInd]) + 'CV = ' + str(CV)

            for ii in range(int(max(wantedNums[fiberInd], 1))):



                for poleInd in range(poles):

                    # wantedPeakInd = (electrodeDistance + poleInd*poleDistance) / CV / dt + jitterAmp*np.random.uniform(-1,1) / dt
                    wantedPeakInd = (electrodeDistance + poleInd * poleDistance + np.random.uniform(0, 1) * jitterDist) / CV / dt
                    # wantedPeakInd = 10/dt


                    difference = peakInd - wantedPeakInd

                    # make peak come earlier
                    if difference > 0:
                        paddedSignal = currentSFAP[difference:]
                    else:
                        paddedSignal = np.concatenate((np.zeros(np.abs(difference)), currentSFAP))

                    if len(paddedSignal) < nRecording:
                        paddedSignal = np.concatenate((paddedSignal, np.zeros(nRecording - len(paddedSignal))))
                    else:
                        paddedSignal = paddedSignal[:nRecording]

                    CAP = np.add(CAP, polePolarities[poleInd] * paddedSignal)
                    # plt.plot(paddedSignal)
                    # plt.title(str(diameters[fiberInd]))
                    # plt.show()

    # plt.plot(tCAP, CAP/np.max(CAP), label=fieldStrings[fieldTypeInd])

    # get the poles and zeros from matlab
    # num = [1/6053445140625000000000000,-1/74733890625000000000,+1/2214337500000000,-1/123018750000,+1/12150000,-1/2250,+1]
    # denum = [1/15625000000000000000000,-3/1562500000000000000,+3/125000000000000,-1/6250000000, 3/5000000,-3/2500, 1]

    num = [1./9938375000000,-(3.)/462250000,+(3.)/21500,-1]
    denum = [1./27000000000,-1./3000000,+1./1000,-1]

    # num = [-18160993481857.9]
    # denum = [1, 1.14384031490999e-06, -6960.76247988057, -0.00799087266204879, 173188542.754159, 17.6610164642334,
    #          -289826464890.561]

    # denum = [1]
    # num = [1, 100]
    #
    # from scipy import signal
    #
    # w, h = freqz(num, denum)
    # fs = 1./dt
    # f = fs * w / (2 * np.pi)

    # # w, h = signal.freqz(num, denum)
    # plt.plot(f, 20 * np.log10(abs(h)))
    # plt.xscale('log')
    # plt.title('Butterworth filter frequency response')
    # plt.xlabel('Frequency [radians / second]')
    # plt.ylabel('Amplitude [dB]')
    # plt.show()

    # b = (1./7840000, 1./ 1400, 1)
    #
    # filteredCAP = lfilter(b, 1, CAP)
    # plt.plot(tCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)], filteredCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)]/np.max(filteredCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)]), label='Matlab')
    # plt.plot(tCAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)],
    #          CAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)] / np.max(
    #              CAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)]), label='non filtered')
    # plt.title('matlab filtered')
    # plt.show()

    # filter
    cutoff = 2800/(2*np.pi) # 300 #

    # plt.plot(tCAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)],
    #          CAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)] / np.max(
    #              CAP[np.logical_and(tCAP > timePlotMin, tCAP < timePlotMax)]), ':', label='no filter')
    for order in [2,3]:
        filteredCAP = butter_lowpass_filter(CAP, cutoff, 1000./dt, order=order)
        plt.plot(tCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)], filteredCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)]/np.max(filteredCAP[np.logical_and(tCAP>timePlotMin, tCAP<timePlotMax)]), label='order='+str(order))

    plt.title('Comparison between experimental data and simulation')
    plt.ylabel('$V_{ext}$ [mV]')


    # from scipy import signal
    #
    # b, a = signal.butter(4, 10 / (np.pi / dt), 'low', analog=False)
    #
    # # plt.figure()
    # # w, h = signal.freqz(b, a)
    # # plt.plot(w, 20 * np.log10(abs(h)))
    # # plt.xscale('log')
    # # plt.title('Butterworth filter frequency response')
    # # plt.xlabel('Frequency [radians / second]')
    # # plt.ylabel('Amplitude [dB]')
    # # plt.margins(0, 0.1)
    # # plt.grid(which='both', axis='both')
    # # # plt.axvline(100, color='green')  # cutoff frequency
    # # plt.show()
    #
    # y = signal.filtfilt(b, a, CAP)
    # plt.plot(tCAP, y)

    # timesTicks = np.arange(5, int(max(tCAP)), 5)
    # tickLabelStrings = []
    # for tickTime in timesTicks:
    #     tickLabelStrings.append('%2.3f' % (electrodeDistance / tickTime))
    #
    # plt.xticks(timesTicks, rotation='vertical')
    # plt.gca().set_xticklabels(tickLabelStrings)
    # plt.xlabel('conduction velocity [m/s]')
    plt.xlabel('time [ms]')

plt.grid()
plt.legend()

plt.show()

# jet = plt.get_cmap('jet')
# cNorm = colors.Normalize(vmin=0, vmax=numFibers - 1)
# scalarMap = cm.ScalarMappable(norm=cNorm, cmap=jet)
#
# for fiberInd in range(numFibers):
#     colorVal = scalarMap.to_rgba(fiberInd)
#
#     plt.plot(t[t>tArtefact], SFAP[t>tArtefact, fiberInd], color=colorVal)
# plt.show()