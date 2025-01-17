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
from turbogenius.lrdmc_genius import LRDMC_genius
from turbogenius.utils_workflows.env import turbo_genius_root

# LRDMC
prefix="lrdmc"
example_root_dir=os.path.join(turbo_genius_root, "examples", "turbogenius_examples")
if os.path.isdir(os.path.join(example_root_dir, prefix)):
    shutil.rmtree(os.path.join(example_root_dir, prefix))
shutil.copytree(os.path.join(example_root_dir, "all_input_files", prefix), os.path.join(example_root_dir, prefix))
os.chdir(os.path.join(example_root_dir, prefix))

lrdmc_genius = LRDMC_genius(
    fort10="fort.10",
    lrdmcsteps=100,
    num_walkers=5,
    alat=-0.4,
    etry=-1.00,
    twist_average=False,
    force_calc_flag=False,
    nonlocalmoves="dlatm" # tmove, dla, dlatm
)

lrdmc_genius.generate_input()
lrdmc_genius.run()
lrdmc_genius.compute_energy_and_forces(bin_block=5, warmupblocks=5, correcting_factor=2)
logger.info(lrdmc_genius.energy)
logger.info(lrdmc_genius.energy_error)