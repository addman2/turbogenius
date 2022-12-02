#!python
# -*- coding: utf-8 -*-

"""

Makefort10 related classes and methods

Todo:
    * refactoring assert sentences. The assert should not be used for any on-the-fly check.

"""

#python modules
import os, sys
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import click
import glob
import pickle
from typing import Union

#pyturbo modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pyturbo.utils.utility import return_atomic_number
from pyturbo.makefort10 import Makefort10
from pyturbo.structure import Structure
from pyturbo.pseudopotentials import Pseudopotentials
from pyturbo.basis_set import Jas_Basis_sets, Det_Basis_sets

#turbo-genius modules
from utils_workflows.env import turbo_genius_root, turbo_genius_tmp_dir
from utils_workflows.utility import prompt
from database_setup import database_setup
from database_setup import all_electron_basis_set_list, ccECP_basis_set_list, BFD_basis_set_list
from database_setup import ecp_list
from geniusIO import GeniusIO

#Logger
from logging import config, getLogger, StreamHandler, Formatter
logger = getLogger('Turbo-Genius').getChild(__name__)
#logger = getLogger(__name__)

from turbo_genius_cli import cli, decorate_grpost, header
@cli.command(short_help = "makefort10_genius")
@decorate_grpost
@click.option("-str", "structure_file",
              help= 'Specify a structure file.',
              default = None,
              type = str)
@click.option("-s", "supercell",
              help= 'Specify a supercell.',
              nargs = 3,
              default = [1,1,1],
              type = int)
@click.option("-detbasis", "det_basis_sets",
              help= f'Specify a basis set for the determinant part. '
                    f'For all-electrons:{all_electron_basis_set_list}. '
                    f'For PPs: ccECP:{ccECP_basis_set_list}, BFD:{BFD_basis_set_list}',
              default = "cc-pVTZ",
              type=click.Choice(all_electron_basis_set_list+ccECP_basis_set_list+BFD_basis_set_list)
              )
@click.option("-jasbasis", "jas_basis_sets",
              help= f'Specify a basis set for the Jastrow part {all_electron_basis_set_list}',
              default = "cc-pVDZ",
              type=click.Choice(all_electron_basis_set_list+ccECP_basis_set_list+BFD_basis_set_list)
              )
@click.option("-detcont", "det_contracted_flag",
              help= 'Contraction flag for the determinant part',
              is_flag=True,
              type=bool
              )
@click.option("-jascont", "jas_contracted_flag",
              help= 'Contraction flag for the jastrow part',
              is_flag=True,
              type=bool
              )
@click.option("-jasallele", "all_electron_jas_basis_set",
              help= 'all-electron flag for the jastrow basis set',
              is_flag=True,
              type=bool
              )
@click.option("-pp", f"pseudo_potential",
              help= f'Pseudopotential, {ecp_list} implemented.',
              default = None,
              type=click.Choice(ecp_list)
              )
@click.option("-detcutbasis", "det_cut_basis_option",
              help= 'Cutting the determinant basis set according to a default criteria',
              is_flag=True,
              type=bool
              )
@click.option("-jascutbasis", "jas_cut_basis_option",
              help= 'Cutting the jastrow basis set according to a default criteria',
              is_flag=True,
              type=bool
              )
@click.option("-complex", "complex",
              help= 'Flag for complex WF',
              is_flag=True,
              default=False,
              type=bool
              )
@click.option("-phaseup", "phaseup",
              help= 'phase, e.g. 0.0 0.0 0.0',
              nargs=3,
              default=[0.0,0.0,0.0],
              type=float
              )
@click.option("-phasedn", "phasedn",
              help= 'phase, e.g. 0.0 0.0 0.0',
              nargs=3,
              default=[0.0,0.0,0.0],
              type=float
              )
@click.option("-neldiff", "neldiff",
              help= 'Diff. between up and dn electrons',
              default=0,
              type=int
              )
@header
def makefort10(
            g:bool,r:bool,post:bool,
            operation:bool,
            log_level:str,
            structure_file:str,
            supercell:list,
            det_basis_sets:str,
            jas_basis_sets:str,
            det_contracted_flag:bool,
            jas_contracted_flag:bool,
            all_electron_jas_basis_set:bool,
            pseudo_potential:Union[str,None],
            det_cut_basis_option:bool,
            jas_cut_basis_option:bool,
            complex:bool,
            phaseup:list,
            phasedn:list,
            neldiff:int
) -> None:
    """makefort10

    makefort10 class launched by turbogenius_cli

        Args:
            See Makefort10_genius arguments.

    """
    pkl_name="makefort10_genius_cli.pkl"
    root_dir=os.getcwd()
    pkl_file=os.path.join(root_dir, pkl_name)

    if pseudo_potential is not None:
        logger.warning("If you want to use all-electron basis for the Jastrow part, plz. use --jasallele option")
    if g:
        os.chdir(root_dir)
        makefort10_genius=Makefort10_genius(
            structure_file=structure_file,
            supercell=supercell,
            det_basis_set=det_basis_sets,
            jas_basis_set=jas_basis_sets,
            det_contracted_flag=det_contracted_flag,
            jas_contracted_flag=jas_contracted_flag,
            all_electron_jas_basis_set=all_electron_jas_basis_set,
            pseudo_potential=pseudo_potential,
            det_cut_basis_option=det_cut_basis_option,
            jas_cut_basis_option=jas_cut_basis_option,
            complex=complex,
            phase_up = phaseup,
            phase_dn = phasedn,
            neldiff = neldiff
        )
        makefort10_genius.generate_input()

        with open(pkl_file, "wb") as f:
            pickle.dump(makefort10_genius, f)

    if r:
        os.chdir(root_dir)
        try:
            with open(pkl_file, "rb") as f:
                makefort10_genius=pickle.load(f)
        except FileNotFoundError:
            logger.error("Did you generate your input file using turbogenius?")
            raise FileNotFoundError
        makefort10_genius.run()

    if post:
        os.chdir(root_dir)
        try:
            with open(pkl_file, "rb") as f:
                makefort10_genius=pickle.load(f)
        except FileNotFoundError:
            logger.error("Did you generate your input file using turbogenius?")
            raise FileNotFoundError
        flags=makefort10_genius.check_results()
        if all(flags):
            logger.info("Job was successful.")
        else:
            logger.info("Job was failure. See the output file.")
            return

        logger.info("Rename the generated fort.10_new as fort.10")
        shutil.move("fort.10_new", "fort.10")

class Makefort10_genius(GeniusIO):
    """

    This class is a wrapper of pyturbo makefort10 class

    Attributes:
         structure_file (str): File name of the input structure, formats suppored by ASE are supported.
         supercell (list):  3 integers, supercell sizes [x,y,z]
         det_basis_set (str or list): basis set for the determinant part: e.g., "cc-pVQZ" (str), a list of gamess format basis sets is accepatable.
         jas_basis_set (str or list): basis set for the Jastrow part: e.g., "cc-pVQZ" (str), a list of gamess format basis sets is accepatable.
         det_contracted_flag (bool): if True determinant basis set is contracted, if False determinant basis set is uncontracted.
         jas_contracted_flag (bool): if True Jastrow basis set is contracted, if False Jastrow basis set is uncontracted.
         all_electron_jas_basis_set (bool): if True Jastrow basis set is read from the specified all-electron basis, if False, pseudo potential ones.
         pseudo_potential (str, list or None): if None, all-electron calculations, if "str", the corresponding PP is read from the database.
         det_cut_basis_option (bool): if True, determinant basis set is cut according to the Andrea Zen's procedure.
         jas_cut_basis_option (bool): if True, Jastrow basis set is cut according to the Andrea Zen's procedure.
         jastrow_type (int): One- and Two- Jastrow type specified.
         complex (bool): if True, the WF is complex, if False, the WF is real.
         phase_up (list): 3-float numbers for the up-phase [x, y, z].
         phase_dn (list): 3-float numbers for the dn-phase [x, y, z].
         neldiff (int): The number of difference between up and dn electrons.
    """
    def __init__(self,
                 structure_file:str,
                 supercell:list=[1, 1, 1],
                 det_basis_set:Union[str,list] = "cc-pVQZ",
                 jas_basis_set:Union[str,list]= "cc-pVQZ",
                 det_contracted_flag:bool = True,
                 jas_contracted_flag:bool = True,
                 all_electron_jas_basis_set:bool = True,
                 pseudo_potential:Union[str,None] = None,
                 det_cut_basis_option:bool = False,
                 jas_cut_basis_option:bool = False,
                 jastrow_type:int=-6,
                 complex:bool=False,
                 phase_up:list=[0.0, 0.0, 0.0],
                 phase_dn:list=[0.0, 0.0, 0.0],
                 neldiff:int=0
                 ):

        self.structure_file = structure_file
        self.supercell = supercell
        self.det_basis_set = det_basis_set
        self.jas_basis_set = jas_basis_set
        self.all_electron_jas_basis_set = all_electron_jas_basis_set
        self.pseudo_potential = pseudo_potential
        self.det_cut_basis_option = det_cut_basis_option
        self.jas_cut_basis_option = jas_cut_basis_option
        self.neldiff=neldiff
        self.complex = complex
        self.phase_up = phase_up
        self.phase_dn = phase_dn

        # makefort10 class
        structure = Structure.parse_structure_from_file(file=structure_file)
        namelist = Makefort10.read_default_namelist(structure=structure, jastrow_type=jastrow_type)

        # set supercell size
        assert len(self.supercell) == 3
        namelist.set_parameter(parameter="nxyz(1)", value=self.supercell[0], namelist="&system")
        namelist.set_parameter(parameter="nxyz(2)", value=self.supercell[1], namelist="&system")
        namelist.set_parameter(parameter="nxyz(3)", value=self.supercell[2], namelist="&system")

        if pseudo_potential is None:
            logger.info("All-electron calculation")
            database_setup(database="BSE")
        elif isinstance(pseudo_potential, str):
            logger.info("Pseudo potential calculation.")
            database_setup(database=pseudo_potential) # for Determinant
            database_setup(database="BSE") # for Jastrow
        elif isinstance(pseudo_potential, list):
            logger.info("Pseudo potential calculation. PPs are given")
        else:
            raise ValueError

        def database_founder(data_sets_list, element, data_choice, prefix="basis_set"):
            if len(data_sets_list) == 0:
                logger.error(f"The chosen {prefix} is not found in the database!!")
                raise NotImplementedError
            elif len(data_sets_list) == 1:
                data_set_found = data_sets_list[0]
                logger.info(f"The chosen {prefix} is found, {os.path.basename(data_set_found)}")
                return data_set_found, data_choice
            else:  # >= 2
                if element not in data_choice.keys():
                    logger.info(f"More than two {prefix}s are found!")
                    def checker(choice):
                        try:
                            if int(choice) in range(len(data_sets_list)):
                                return True
                            else:
                                return False
                        except ValueError:
                            return False

                    b_list_shown = [f'{i}:{os.path.basename(d)}' for i, d in enumerate(data_sets_list)]
                    b_index = int(prompt(f"Choose one of them, 0,1,.. from {b_list_shown}:", checker=checker))
                    data_set_found = data_sets_list[b_index]
                    data_choice[element]=data_set_found
                    logger.info(f"The chosen {prefix} is {os.path.basename(data_set_found)}")
                    return data_set_found, data_choice

                else:
                    data_set_found = data_choice[element]
                    logger.info(f"The chosen {prefix} is found, {os.path.basename(data_set_found)}")
                    return data_set_found, data_choice

        # note! element_symbols depends on the number of supercell size!!!
        # note! for the basis part, do not use element_symbols_supercell, but use structure.element_symbols
        element_symbols_supercell = structure.element_symbols * self.supercell[0] * self.supercell[1] * self.supercell[2]

        # det. basis set!
        if isinstance(det_basis_set, str):
            det_basis_files = []; det_basis_choice = {}
            for element in structure.element_symbols:
                if pseudo_potential is None: # all-electron
                    det_basis_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "basis_set", "BSE", f"{element}_{det_basis_set}*.basis"))
                    det_basis_chosen, det_basis_choice = database_founder(data_sets_list=det_basis_sets_list, element=element, data_choice=det_basis_choice, prefix="basis_set")
                else: # pseudo potential calculation
                    det_basis_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "basis_set", pseudo_potential, f"{element}_{det_basis_set}*.basis"))
                    det_basis_chosen, det_basis_choice = database_founder(data_sets_list=det_basis_sets_list, element=element, data_choice=det_basis_choice, prefix="basis_set")
                det_basis_files.append(det_basis_chosen)

            det_basis_sets = Det_Basis_sets.parse_basis_sets_from_gamess_format_files(files=det_basis_files)

        elif isinstance(det_basis_set, list):
            logger.info("Basis sets for the det. parts are given")
            det_basis_sets = Det_Basis_sets.parse_basis_sets_from_texts(texts=det_basis_set, format="gamess")

        else:
            raise ValueError

        # jas. basis set
        if isinstance(jas_basis_set, str):
            jas_basis_files = []; jas_basis_choice = {}
            for element in structure.element_symbols:
                if pseudo_potential is None: # all-electron
                    jas_basis_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "basis_set", "BSE", f"{element}_{jas_basis_set}*.basis"))
                    jas_basis_chosen, jas_basis_choice = database_founder(data_sets_list=jas_basis_sets_list, element=element, data_choice=jas_basis_choice, prefix="basis_set")
                else: # pseudo potential calculation
                    if self.all_electron_jas_basis_set:
                        jas_basis_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "basis_set", "BSE", f"{element}_{jas_basis_set}*.basis"))
                        logger.info(jas_basis_sets_list)
                        jas_basis_chosen, jas_basis_choice = database_founder(data_sets_list=jas_basis_sets_list, element=element, data_choice=jas_basis_choice, prefix="basis_set")
                    else:
                        jas_basis_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "basis_set", pseudo_potential, f"{element}_{jas_basis_set}*.basis"))
                        jas_basis_chosen, jas_basis_choice = database_founder(data_sets_list=jas_basis_sets_list, element=element, data_choice=jas_basis_choice, prefix="basis_set")
                jas_basis_files.append(jas_basis_chosen)

            jas_basis_sets = Jas_Basis_sets.parse_basis_sets_from_gamess_format_files(files=jas_basis_files)

        elif isinstance(jas_basis_set, list):
            logger.info("Basis sets for the Jastrow parts are given")
            jas_basis_sets = Jas_Basis_sets.parse_basis_sets_from_texts(texts=jas_basis_set, format="gamess")

        else:
            raise ValueError

        # pseudo potential
        if pseudo_potential is None: # all-electron
            pp_files = []; pp_choice = {}
            for element in element_symbols_supercell:
                pp_files.append(None)
            pseudo_potentials = Pseudopotentials.parse_pseudopotential_from_gamess_format_files(pp_files)

        else:
            if isinstance(pseudo_potential, str):
                pp_files = []; pp_choice = {}
                for element in element_symbols_supercell:
                    if pseudo_potential is None: # all-electron
                        pp_chosen=None
                    else: # pseudo potential calculation
                        #if self.all_electron_jas_basis_set:
                        pp_sets_list=glob.glob(os.path.join(turbo_genius_tmp_dir, "pseudo_potential", pseudo_potential, f"{element}_{pseudo_potential}*.pseudo"))
                        pp_chosen, pp_choice = database_founder(data_sets_list=pp_sets_list, element=element, data_choice=pp_choice, prefix="pseudo_potential")
                    pp_files.append(pp_chosen)
                pseudo_potentials = Pseudopotentials.parse_pseudopotential_from_gamess_format_files(pp_files)

            elif isinstance(pseudo_potential, list):
                pseudo_potentials = Pseudopotentials.parse_pseudopotential_from_gamess_format_texts(texts=pseudo_potential)

            else:
                raise ValueError

            pseudo_potentials.set_cutoffs()

    # contracted -> uncontracted
        if not det_contracted_flag:
            logger.info("Contracted -> Uncontracted, Det. part.")
            det_basis_sets.contracted_to_uncontracted()

        if not jas_contracted_flag:
            logger.info("Contracted -> Uncontracted, Jas. part.")
            jas_basis_sets.contracted_to_uncontracted()

        if det_cut_basis_option:
            logger.info("cutbasis for Det. part.")
            # cut basis, det_basis, according to Andrea Zen's criteria, exponents > 8 * Z^2
            for nuc, element in enumerate(structure.element_symbols):
                thr_exp= 8 * return_atomic_number(element) ** 2
                det_basis_sets.cut_orbitals(thr_exp=thr_exp, nucleus_index=nuc, method="larger")
        if jas_cut_basis_option:
            logger.info("cutbasis for Jas. part.")
            # cut basis, jas_basis, according to max criteria, exponents > max (det part)
            for nuc, element in enumerate(structure.element_symbols):
                # to be refactored!! Is this appropriate for the Jastrow part??
                thr_exp= 4 * return_atomic_number(element) # not 8*Z**2 but 4*Z
                jas_basis_sets.cut_orbitals(thr_exp=thr_exp, nucleus_index=nuc, method="larger")
                thr_angmom = jas_basis_sets.get_largest_angmom(nucleus_index=nuc)
                jas_basis_sets.cut_orbitals(thr_angmom=thr_angmom, nucleus_index=nuc, method="larger-angmom")
        else:
            pass

        assert len(self.phase_up) == 3
        assert len(self.phase_dn) == 3

        namelist.set_parameter(parameter="phase(1)", value=self.phase_up[0], namelist="&system")
        namelist.set_parameter(parameter="phase(2)", value=self.phase_up[1], namelist="&system")
        namelist.set_parameter(parameter="phase(3)", value=self.phase_up[2], namelist="&system")
        namelist.set_parameter(parameter="phasedo(1)", value=self.phase_dn[0], namelist="&system")
        namelist.set_parameter(parameter="phasedo(2)", value=self.phase_dn[1], namelist="&system")
        namelist.set_parameter(parameter="phasedo(3)", value=self.phase_dn[2], namelist="&system")

        # neldiff
        namelist.set_parameter(parameter="neldiff", value=self.neldiff, namelist="&electrons")

        if complex:
            det_basis_sets.real_to_complex()
            namelist.set_parameter(parameter="complexfort10", value='.true.', namelist="&system")

        self.makefort10 = Makefort10(
            structure=structure,
            det_basis_sets=det_basis_sets,
            jas_basis_sets=jas_basis_sets,
            pseudo_potentials=pseudo_potentials,
            namelist=namelist
        )

        self.makefort10.sanity_check()

    def run_all(self, input_name:str="makefort10.input",  output_name:str="out_make", basis_sets_unique_element:bool=True) -> None :
        """
            Generate input files and run the command.

            Args:
                input_name (str): input file name
                output_name (str): output file name
                basis_sets_unique_element (bool): if True, the same basis set is assigned for atoms with the same elemental type.
        """
        self.makefort10.generate_input(input_name=input_name, basis_sets_unique_element=basis_sets_unique_element)
        self.makefort10.run(input_name=input_name, output_name=output_name)

    def generate_input(self, input_name:str="makefort10.input", basis_sets_unique_element:bool=True) -> None:
        """
            Generate input file.

            Args:
                input_name (str): input file name
                basis_sets_unique_element (bool): if True, the same basis set is assigned for atoms with the same elemental type.
        """
        self.makefort10.generate_input(input_name=input_name, basis_sets_unique_element=basis_sets_unique_element)

    def run(self, input_name:str="makefort10.input", output_name:str="out_make") -> None:
        """
            Run the command.

            Args:
                input_name (str): input file name
                output_name (str): output file name
        """
        self.makefort10.run(input_name=input_name, output_name=output_name)

    def check_results(self, output_names:list=["out_make"]) -> bool:
        """
            Check the result.

            Args:
                output_names (list): a list of output file names
            Return:
                bool: True if all the runs were successful, False if an error is detected in the files.
        """
        return self.makefort10.check_results(output_names=output_names)

if __name__ == "__main__":
    logger = getLogger("Turbo-Genius")
    logger.setLevel("INFO")
    logger_p = getLogger("pyturbo")
    logger_p.setLevel("INFO")
    stream_handler = StreamHandler()
    stream_handler.setLevel("INFO")
    handler_format = Formatter('%(name)s - %(levelname)s - %(lineno)d - %(message)s')
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)
    logger_p.addHandler(stream_handler)

    from utils_workflows.env import turbo_genius_root

    os.chdir(os.path.join(turbo_genius_root, "tests", "makefort10"))

    # moved to examples

