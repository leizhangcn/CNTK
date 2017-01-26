﻿# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

import numpy as np
import os
import sys
import platform
from shutil import copyfile
from cntk.io import ReaderConfig, ImageDeserializer, FULL_DATA_SWEEP
from cntk import distributed
from cntk.device import set_default_device, gpu

abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(abs_path, "..", "..", "..", "..", "Examples", "Image", "Classification", "ConvNet", "Python"))
from ConvNet_CIFAR10_DataAug_Distributed import convnet_cifar10_dataaug

def run_cifar_convnet_distributed():
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             *"../../../../Examples/Image/DataSets/CIFAR-10".split("/"))
    base_path = os.path.normpath(base_path)
    
    # If {train,test}_map.txt don't exist locally, copy to local location
    if (not(os.path.isfile(os.path.join(base_path, 'train_map.txt')) and os.path.isfile(os.path.join(base_path, 'test_map.txt')))): 
        # copy from backup location 
        base_path_bak = os.path.join(os.environ['CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY'],
                                     *"Image/CIFAR/v0/cifar-10-batches-py".split("/"))
        base_path_bak = os.path.normpath(base_path_bak)
        
        copyfile(os.path.join(base_path_bak, 'train_map.txt'), os.path.join(base_path, 'train_map.txt'))
        copyfile(os.path.join(base_path_bak, 'test_map.txt'), os.path.join(base_path, 'test_map.txt'))
        if (not(os.path.isdir(os.path.join(base_path, 'cifar-10-batches-py')))): 
            os.mkdir(os.path.join(base_path, 'cifar-10-batches-py'))
        copyfile(os.path.join(base_path_bak, 'data.zip'), os.path.join(base_path, 'cifar-10-batches-py', 'data.zip'))
        copyfile(os.path.join(base_path_bak, 'CIFAR-10_mean.xml'), os.path.join(base_path, 'CIFAR-10_mean.xml'))
    
    # change dir to locate data.zip correctly
    os.chdir(base_path)

    from _cntk_py import set_computation_network_trace_level, set_fixed_random_seed, force_deterministic_algorithms
    set_computation_network_trace_level(1) 
    set_fixed_random_seed(1)  # BUGBUG: has no effect at present  # TODO: remove debugging facilities once this all works
    #force_deterministic_algorithms()
    # TODO: do the above; they lead to slightly different results, so not doing it for now

    train_data = os.path.join(base_path, 'train_map.txt')
    mean_data = os.path.join(base_path, 'CIFAR-10_mean.xml')
    test_data = os.path.join(base_path, 'test_map.txt')

    num_quantization_bits = 32
    return convnet_cifar10_dataaug(train_data, test_data, mean_data, num_quantization_bits, epoch_size=512, max_epochs=2)

if __name__=='__main__':
    assert distributed.Communicator.rank() < distributed.Communicator.num_workers()
    set_default_device(gpu(0)) # force using GPU-0 in test for speed
    run_cifar_convnet_distributed()
    distributed.Communicator.finalize()
