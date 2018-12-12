#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 15:42:12 2018

@author: wanglab
"""

import os, sys, shutil
import argparse   
from utils.preprocessing.preprocess import get_dims_from_folder, make_indices, make_memmap_from_tiff_list, generate_patch, reconstruct_memmap_array_from_tif_dir
from utils.postprocessing.cell_stats import calculate_cell_measures, consolidate_cell_measures    
import pandas as pd, numpy as np


def main(**args):
    
    #args should be the info you need to specify the params
    # for a given experiment, but only params should be used below
    params = fill_params(**args)
    
    if params["stepid"] == 0:
        #######################################PRE-PROCESSING FOR CNN INPUT --> MAKING INPUT ARRAY######################################################
        
        #make directory to store patches
        if not os.path.exists(params["data_dir"]): os.mkdir(params["data_dir"])
    	#save params to .csv file
        save_params(params, params["data_dir"])
        
        #convert full size data folder into memmap array
        make_memmap_from_tiff_list(params["cellch_dir"], params["data_dir"], 
                                               params["cores"], params["dtype"], params["verbose"])
            
    if params["stepid"] == 1:
        #######################################PRE-PROCESSING FOR CNN INPUT --> PATCHING###################################################
        
        #generate memmap array of patches
        patch_dst = generate_patch(**params)
        sys.stdout.write("\nmade patches in {}\n".format(patch_dst)); sys.stdout.flush()

    elif params["stepid"] == 21:
        ####################################POST CNN --> INITIALISING RECONSTRUCTED ARRAY FOR ARRAY JOB####################################
        
        sys.stdout.write("\ninitialising reconstructed array...\n"); sys.stdout.flush()
        np.lib.format.open_memmap(params["reconstr_arr"], mode="w+", shape = params["inputshape"], dtype = params["dtype"])
        sys.stdout.write("done :]\n"); sys.stdout.flush()

    elif params["stepid"] == 2:
        #####################################POST CNN --> RECONSTRUCTION AFTER RUNNING INFERENCE ON TIGER2#################################
        
        #reconstruct
        sys.stdout.write("\nstarting reconstruction...\n"); sys.stdout.flush()
        reconstruct_memmap_array_from_tif_dir(**params)
        if params["cleanup"]: shutil.rmtree(params["cnn_dir"])

    elif params["stepid"] == 3:
        ##############################################POST CNN --> FINDING CELL CENTERS#####################################################   
        
        #find cell centers, measure sphericity, perimeter, and z span of a cell
        csv_dst = calculate_cell_measures(**params)
        sys.stdout.write("\ncell coordinates and measures saved in {}\n".format(csv_dst)); sys.stdout.flush()
        
    elif params["stepid"] == 4:
        ##################################POST CNN --> CONSOLIDATE CELL CENTERS FROM ARRAY JOB##############################################
        
        #part 1 - check to make sure all jobs that needed to run have completed; part 2 - make pooled results
        consolidate_cell_measures(**params)


def fill_params(expt_name, stepid, jobid):

    params = {}

    #slurm params
    params["stepid"]        = stepid
    params["jobid"]         = jobid 
    
    #experiment params
    params["expt_name"]     = os.path.basename(os.path.abspath(expt_name))
        
    #find cell channel tiff directory
    fsz = os.path.join(expt_name, "full_sizedatafld")
    vols = os.listdir(fsz); vols.sort()
    src = os.path.join(fsz, vols[len(vols)-1]) #hack - try to load param_dict instead?
    if not os.path.isdir(src): src = os.path.join(fsz, vols[len(vols)-2]) 
    
    params["cellch_dir"]    = src
    params["scratch_dir"]   = "/jukebox/scratch/zmd"
    params["data_dir"]      = os.path.join(params["scratch_dir"], params["expt_name"])
    
    #changed paths after cnn run
    params["cnn_data_dir"]  = os.path.join(params["scratch_dir"], params["expt_name"])
    params["cnn_dir"]       = os.path.join(params["cnn_data_dir"], "output_chnks") #set cnn patch directory
    params["reconstr_arr"]  = os.path.join(params["cnn_data_dir"], "reconstructed_array.npy")
    params["output_dir"]    = expt_name
    
    #pre-processing params
    params["dtype"]         = "float32"
    params["cores"]         = 8
    params["verbose"]       = True
    params["cleanup"]       = False
    
    params["patchsz"]       = (64, 3840, 3328) #cnn window size for lightsheet = typically 20, 192, 192
    params["stridesz"]      = (44, 3648, 3136) 
    params["window"]        = (20, 192, 192)
    
    params["inputshape"]    = get_dims_from_folder(src)
    params["patchlist"]     = make_indices(params["inputshape"], params["stridesz"])
    
    #post-processing params
    params["threshold"]     = (0.6,1)
    params["zsplt"]         = 30
    params["ovlp_plns"]     = 30
        
    return params

def save_params(params, dst):
    """ 
    save params in cnn specific parameter dictionary for reconstruction/postprocessing 
    can discard later if need be
    """
    (pd.DataFrame.from_dict(data=params, orient="index").to_csv(os.path.join(dst, "cnn_param_dict.csv"),
                            header = False))
    sys.stdout.write("\nparameters saved in: {}".format(os.path.join(dst, "cnn_param_dict.csv"))); sys.stdout.flush()
    
#%%
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument("stepid", type=int,
                        help="Step ID to run patching, reconstructing, or cell counting")
    parser.add_argument("jobid",
                        help="Job ID to run patching as an array job")
    parser.add_argument("expt_name",
                        help="Tracing output directory (aka registration output)")
    
    args = parser.parse_args()
    
    main(**vars(args))
            
