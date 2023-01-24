import time
import multiprocessing as mp
import threading
import os
import numpy as np
import concurrent.futures


def do_something(sec):
    print(f'Sleeping {sec} second(s)...')
    time.sleep(sec)
    return 'Done Sleeping'
    


if __name__ == '__main__':

    start = time.perf_counter()
    
    '''     
    processes = []
   
    for _ in range(10):
        p = mp.Process(target=do_something, args=[1.5])
        p.start()
        processes.append(p)
    
    for process in processes:
        process.join()
    '''
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.submit(do_something, 1)
            
    finish = time.perf_counter()
    
    print(f'Finished in {round(finish-start, 2)} second(s)!')
