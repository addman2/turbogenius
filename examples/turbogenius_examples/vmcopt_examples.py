#!python
# -*- coding: utf-8 -*-

#python modules
import os, sys
import shutil

#set logger
from logging import config, getLogger, StreamHandler, Formatter
logger = getLogger('pyturbo')
logger.setLevel("DEBUG")
stream_handler = StreamHandler()
stream_handler.setLevel("DEBUG")
handler_format = Formatter('%(name)s - %(levelname)s - %(lineno)d - %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)

#pyturbo modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from turbogenius.vmc_opt_genius import VMCopt_genius
from turbogenius.utils_workflows.env import turbo_genius_root

# vmcopt
prefix="vmcopt"
example_root_dir=os.path.join(turbo_genius_root, "examples", "turbogenius_examples")
if os.path.isdir(os.path.join(example_root_dir, prefix)):
    shutil.rmtree(os.path.join(example_root_dir, prefix))
shutil.copytree(os.path.join(example_root_dir, "all_input_files", prefix), os.path.join(example_root_dir, prefix))
os.chdir(os.path.join(example_root_dir, prefix))

vmcopt_genius=VMCopt_genius(
            fort10="fort.10",
            vmcoptsteps=500,
            steps=10,
            bin_block=1,
            warmupblocks=0,
            num_walkers=20,
            optimizer="lr",
            learning_rate=0.35,
            regularization=0.001,
            opt_onebody=True,
            opt_twobody=True,
            opt_det_mat=False,
            opt_jas_mat=True,
            opt_det_basis_exp=False,
            opt_jas_basis_exp=False,
            opt_det_basis_coeff=False,
            opt_jas_basis_coeff=False,
            twist_average=False,
            )
vmcopt_genius.generate_input()
vmcopt_genius.run()
vmcopt_genius.get_energy()
vmcopt_genius.average(optwarmupsteps=400)