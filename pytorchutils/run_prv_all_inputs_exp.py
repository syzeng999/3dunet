#!/usr/bin/env python
__doc__ = """

Training Script

Put all the ugly things that change with every experiment here

Nicholas Turner, 2017-8
"""

import os, imp
import collections

import torch
import tensorboardX

import utils
import train
import loss


def main(**args):

    #args should be the info you need to specify the params
    # for a given experiment, but only params should be used below
    params = fill_params(**args)

    utils.set_gpus(params["gpus"])

    utils.make_required_dirs(**params)

    tstamp = utils.timestamp()
    utils.log_params(params, tstamp=tstamp)
    utils.log_tagged_modules(params["modules_used"],
                             params["log_dir"], "train",
                             chkpt_num=params["chkpt_num"],
                             tstamp=tstamp)

    start_training(**params)


def fill_params(expt_name, chkpt_num, batch_sz, gpus,
                sampler_fname, model_fname, augmentor_fname, **args):

    params = {}

    #Model params
    params["in_spec"]	   = dict(input=(1,20,192,192))
    params["output_spec"]  = collections.OrderedDict(cleft=(1,20,192,192))
    params["width"]        = [32, 40, 80]

    #Training procedure params
    params["max_iter"]    = 1000000
    params["lr"]          = 0.00001
    params["test_intv"]   = 100
    params["test_iter"]   = 10
    params["avgs_intv"]   = 50
    params["chkpt_intv"]  = 10
    params["warm_up"]     = 50
    params["chkpt_num"]   = chkpt_num
    params["batch_size"]  = batch_sz

    #Sampling params
    params["data_dir"]     = "/tigress/zmd/3dunet_data/prv/all_inputs/"
    assert os.path.isdir(params["data_dir"]),"nonexistent data directory"
    
    params["train_sets"] = ['zd_ann_prv_jg05_neocortex_z310-449_01',
			 'zd_ann_prv_jg24_neocortex_z300-400_01',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0650-0700_01',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0450-0500_01',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0450-0500_00',
			 'cj_ann_prv_jg05_neocortex_z250-449_02',
			 'zd_ann_prv_jg32_hypothal_z710-810_02',
			 'cj_ann_prv_jg05_hypothal_z661-760_02',
			 'JGANNOTATION_20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_01',
			 'cj_ann_prv_jg29_neocortex_z700-800_02',
			 'cj_ann_prv_jg24_neocortex_z300-400_01',
			 'cj_ann_prv_jg32_neocortex_z650-810_01',
			 '20180305_jg_bl6f_prv_11_647_010na_7d5um_250msec_10povlp_ch00_C00_300-345_00',
			 'JGANNOTATION_20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0450-0500_01',
			 'cj_ann_prv_jg24_neocortex_z300-400_02',
			 'cj_ann_prv_jg24_hypothal_z550-650_01',
			 'cj_ann_prv_jg29_hypothal_z580-700_01',
			 'zd_ann_prv_jg29_neocortex_z300-500_01',
			 '20180305_jg_bl6f_prv_11_647_010na_7d5um_250msec_10povlp_ch00_C00_300-345_01',
			 'zd_ann_prv_jg32_neocortex_z650-810_01',
			 'zd_ann_prv_jg24_hypothal_z550-650_01',
			 '20180215_jg_bl6f_prv_10_647_010na_z7d5um_250msec_10povlap_ch00_z200-400_y4500-4850_x2050-2400',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0650-0700_06',
			 'cj_ann_prv_jg32_hypothal_z650-810_01',
			 '20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_01',
			 'JGANNOTATION_20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0450-0500_02',
			 '20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_03',
			 'cj_ann_prv_jg05_neocortex_z310-449_01']

    params["val_sets"] = ['cj_ann_prv_jg29_hypothal_z700-800_02',
			 'JGANNOTATION_20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_02',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0650-0700_00',
			 '20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_02',
			 'JGANNOTATION_20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_03',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0450-0500_06',
			 '20180306_jg_bl6f_prv_16_647_010na_7d5um_250msec_10povlp_ch00_C00_Z0650-0700_05',
			 '20180305_jg_bl6f_prv_12_647_010na_7d5um_250msec_10povlp_ch00_C00_400-440_00']

    params["patchsz"]	   = (20,192,192)
    params["sampler_spec"] = dict(input=params["patchsz"],
                                  soma_label=params["patchsz"])

    #GPUS
    params["gpus"] = gpus

    #IO/Record params
    params["expt_name"]  = expt_name
    params["expt_dir"]   = "/tigress/zmd/3dunet_data/prv/experiments/{}".format(expt_name)

    params["model_dir"]  = os.path.join(params["expt_dir"], "models")
    params["log_dir"]    = os.path.join(params["expt_dir"], "logs")
    params["fwd_dir"]    = os.path.join(params["expt_dir"], "forward")
    params["tb_train"]   = os.path.join(params["expt_dir"], "tb/train")
    params["tb_val"]     = os.path.join(params["expt_dir"], "tb/val")

    #Use-specific Module imports
    params["model_class"]   = utils.load_source(model_fname).Model
    params["sampler_class"] = utils.load_source(sampler_fname).Sampler
    params["augmentor_constr"] = utils.load_source(augmentor_fname).get_augmentation

    #"Schema" for turning the parameters above into arguments
    # for the model class
    params["model_args"]     = [params["in_spec"], params["output_spec"],
                                params["width"]]
    params["model_kwargs"]   = {}

    #modules used for record-keeping
    params["modules_used"] = [__file__, model_fname, sampler_fname,
                              augmentor_fname, "loss.py"]

    return params


def start_training(model_class, model_args, model_kwargs,
                   sampler_class, sampler_spec, augmentor_constr,
                   chkpt_num, lr, train_sets, val_sets, data_dir,
                   model_dir, log_dir, tb_train, tb_val,
                   **params):

    #PyTorch Model
    net = utils.create_network(model_class, model_args, model_kwargs)
    train_writer = tensorboardX.SummaryWriter(tb_train)
    val_writer = tensorboardX.SummaryWriter(tb_val)
    monitor = utils.LearningMonitor()

    #Loading model checkpoint (if applicable)
    if chkpt_num != 0:
        utils.load_chkpt(net, monitor, chkpt_num, model_dir, log_dir)

    #DataProvider Stuff
    train_aug = augmentor_constr(True)
    train_sampler = utils.AsyncSampler(sampler_class(data_dir, sampler_spec,
                                                     vols=train_sets,
                                                     mode="train",
                                                     aug=train_aug))

    val_aug = augmentor_constr(False)
    val_sampler   = utils.AsyncSampler(sampler_class(data_dir, sampler_spec,
                                                     vols=val_sets,
                                                     mode="val",
                                                     aug=val_aug))

    loss_fn = loss.BinomialCrossEntropyWithLogits()
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)

    train.train(net, loss_fn, optimizer, train_sampler, val_sampler,
                train_writer=train_writer, val_writer=val_writer,
                last_iter=chkpt_num, model_dir=model_dir, log_dir=log_dir,
                monitor=monitor,
                **params)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description= __doc__)

    parser.add_argument("expt_name",
                        help="Experiment Name")
    parser.add_argument("model_fname",
                        help="Model Template filename")
    parser.add_argument("sampler_fname",
                        help="DataProvider Sampler filename")
    parser.add_argument("augmentor_fname",
                        help="Data Augmentor module filename")
    parser.add_argument("--batch_sz",  type=int, default=1,
                        help="Batch size for each sample")
    parser.add_argument("--chkpt_num", type=int, default=0,
                        help="Checkpoint Number")
    parser.add_argument("--gpus", default=["0"], nargs="+")

    args = parser.parse_args()


    main(**vars(args))

