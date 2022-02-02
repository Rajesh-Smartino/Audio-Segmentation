import soundfile as sf
import math
from scipy.signal.windows import hann, hamming
import numpy as np
from matplotlib import pyplot as plt

# Reading the input voice signal using soundfile
signal, fs = sf.read('/Users/rajeshr/Desktop/voice_HDP.wav')
print(signal, fs)


''' 
This functions splits into multiples frames (Enframe as did in lab9). 
Inputs are: 
1. Input signal, fs,
2. Window (can use scipy.signal.windows to import hann, hamming or rect) 
Winsize(nw) is needed nw = 0.03*fs [Typical val 30ms*fs], 
3. Overlap factor (Typical usually 0.5).
Returns: frames.
'''

sym = False
window = hamming(math.floor(0.03*fs), sym)

def split_frames(signal, window, overlap=0.5):
    
    n = len(signal) #length of input
    nw = len(window) #window size
    step = math.floor(nw*(1-overlap)) 
    
    nf = math.floor((n-nw)/step)+1 #number of frames
    
    frames = np.zeros((nf, nw))
    
    for i in range(nf):
        offset = i*step        
        frames[i, :] = window*signal[offset: nw+offset]
    
    return frames
    
frames = split_frames(signal, window, 0.5)
print(len(frames), frames)

'''
Computing energy for each frame
'''
energy = []

for frame in frames:
    enrg = 0
    for i in frame:
        enrg = enrg + abs(i*i)
    energy.append(enrg)
    
print(len(energy))

'''
Visualizing Energy plots
'''
max_energy = max(energy)
x = np.arange(len(energy))
plt.plot(x, energy/max_energy)
plt.xlabel('Frame Index')
plt.ylabel('Normalized Energy')
plt.title('Energy Plot')
plt.show()


'''
Extracting the frame numbers by fixing a threshold value
'''
threshold = 0.1 #Threshold value can be chosen by seeing the energy plot.
segmented_frame_no = []
for i in range(len(energy)):
    if energy[i] > threshold:
        segmented_frame_no.append(i)
    
del segmented_frame_no[0]
print(len(segmented_frame_no), segmented_frame_no)

'''
Grouping the frames numbers into lists
'''
error = 3 # error is the number of index differences to be appended into same segment.
grouped_frame_no = []
temp = []

for i in range(len(segmented_frame_no)-1):
    if segmented_frame_no[i+1] - segmented_frame_no[i] <= error:
        temp.append(segmented_frame_no[i])
    else:
        grouped_frame_no.append(temp)
        temp = []

if temp != 0:
    grouped_frame_no.append(temp)

print(len(grouped_frame_no), grouped_frame_no)

'''
Obtaining the frames from the frame numbers list
'''
segmented_frames = []
for i in range(len(grouped_frame_no)):
    if grouped_frame_no[i]:
        t = grouped_frame_no[i]
        #print(t)
        last = t[-1]
        #print(last+1)
        grouped_frame_no[i].append(last+1)
        segmented_frames.append([frames[k] for k in grouped_frame_no[i]])    
    
''' ######## OVERLAP ADD ########
This functions adds back the multiples frames into single frame. 
Inputs are: 
1. frames,
2. n len of the input signal, obtained while reading input, if not available pass -1
3. Overlap factor (usually 0.5).
Returns: frame.
'''
def merge_frames(frames, n, overlap=0.5):
    
    nf, nw = frames.shape
    step = math.floor(nw*(1-overlap))   
    if n == -1:
        n = (nf-1) * step + nw
    frame = np.zeros(n)

    for i in range(nf):
        offset = i * step
        frame[offset : nw + offset] += frames[i, :]
    
    return frame

'''
Adding back the frames into single frame
'''
segemented_file = []
for frames in segmented_frames:
    frames = np.array(frames)
    segemented_file.append(merge_frames(frames, -1, 0.5))
    
print(segemented_file)

'''
Writting the segmented audio
'''
i = 1
for segment in segemented_file:
    sf.write('/Users/rajeshr/Desktop/AudioSegment/segmented_'+str(i)+'.wav', segment, fs)
    i = i+1