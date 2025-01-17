#!python
# -*- coding: utf-8 -*-

#python modules
import os, sys, shutil

#set logger
from logging import config, getLogger, StreamHandler, Formatter
logger = getLogger('pyturbo')
logger.setLevel("DEBUG")
stream_handler = StreamHandler()
stream_handler.setLevel("DEBUG")
handler_format = Formatter('%(name)s - %(levelname)s - %(lineno)d - %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)

#turbogenius modules
from turbogenius.pyturbo.basis_set import Basis_set, Jas_Basis_sets, Det_Basis_sets
from turbogenius.pyturbo.utils.downloader import BFD, BSE, ccECP
from turbogenius.utils_workflows.env import turbo_genius_root

#basis sets
prefix="basis_sets"
example_root_dir=os.path.join(turbo_genius_root, "examples", "pyturbo_examples")
if os.path.isdir(os.path.join(example_root_dir, prefix)):
    shutil.rmtree(os.path.join(example_root_dir, prefix))
shutil.copytree(os.path.join(example_root_dir, "all_input_files", prefix), os.path.join(example_root_dir, prefix))
basis_sets_test_dir=os.path.join(example_root_dir, prefix)

prefix="pseudo_potentials"
example_root_dir=os.path.join(turbo_genius_root, "examples", "pyturbo_examples")
if os.path.isdir(os.path.join(example_root_dir, prefix)):
    shutil.rmtree(os.path.join(example_root_dir, prefix))
shutil.copytree(os.path.join(example_root_dir, "all_input_files", prefix), os.path.join(example_root_dir, prefix))
pseudo_potential_output_dir=os.path.join(example_root_dir, prefix)

os.chdir(basis_sets_test_dir)

# BFD basis sets
bfd=BFD(basis_sets_output_dir=basis_sets_test_dir, pseudo_potential_output_dir=pseudo_potential_output_dir)
bfd.to_file(element_list=["C"], basis_list=["vqz"])

# BSE all-electron basis sets
bse=BSE(basis_sets_output_dir=basis_sets_test_dir)
bse.to_file(element_list=["Na", "N"], basis_list=["cc-pVQZ"])

# ccECP
#element_list = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"]
element_list = ["H", "He", "Li"]
ccECP = ccECP(basis_sets_output_dir=basis_sets_test_dir, pseudo_potential_output_dir=pseudo_potential_output_dir)
ccECP.to_file(basis_list=["cc-pVDZ"], element_list=element_list)

## basis set classes
bfd=BFD(basis_sets_output_dir=basis_sets_test_dir, pseudo_potential_output_dir=pseudo_potential_output_dir)
if not os.path.isfile("C_vqz.basis"): bfd.to_file(element_list=["C"], basis_list=["vqz"])
if not os.path.isfile("H_vqz.basis"): bfd.to_file(element_list=["H"], basis_list=["vqz"])

os.chdir(basis_sets_test_dir)
basis_set=Basis_set.parse_basis_set_info_from_gamess_format_file("C_vqz.basis")
det_basis_sets=Det_Basis_sets.parse_basis_sets_from_gamess_format_files(files=["C_vqz.basis", "C_vqz.basis", "H_vqz.basis"])
jas_basis_sets=Jas_Basis_sets.parse_basis_sets_from_gamess_format_files(files=["C_vqz.basis", "C_vqz.basis"])
jas_basis_sets.contracted_to_uncontracted() # convert contracted basis sets to uncontracted ones!!

