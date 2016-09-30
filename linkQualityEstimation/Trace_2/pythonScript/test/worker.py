import multiprocessing
import matplotlib.pyplot as plt
import numpy as np

def main():
    pool = multiprocessing.Pool()
    num_figs = 100
    input = zip(np.random.randint(10,1000,num_figs),
                range(num_figs))
    pool.map(plot, input)

def plot(args):
    num, i = args
    fig = plt.figure()
    data = np.random.randn(num).cumsum()
    plt.plot(data)
    plt.title('Plot of a %i-element brownian noise sequence' % num)
    fig.savefig('temp_fig_%02i.png' % i, dpi=1000)

main()
