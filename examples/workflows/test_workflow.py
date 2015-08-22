from __future__ import division, unicode_literals, print_function

"""
This is a simpler verison of single_workflow with just one firework
and firetask.
used only for testing.
Shows how to set a firework's launch directory
"""

import sys

import numpy as np

from pymatgen import Lattice
from pymatgen.core.structure import Structure
from pymatgen.io.vasp.inputs import Incar, Poscar, Potcar, Kpoints

from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks import Firework, Workflow, LaunchPad
from fireworks.core.rocket_launcher import launch_rocket
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter

from mpinterfaces.calibrate import Calibrate
from mpinterfaces.firetasks import MPINTCalibrateTask

a0 = 3.965
lattice_matrix = a0 * np.array([ [0.5, 0.0, 0.5], 
                                 [0.5, 0.5, 0.0], 
                                 [0.0, 0.5, 0.5] ])
lattice = Lattice(lattice_matrix)
structure = Structure( lattice, ['Pt'], 
                       [ [0.0, 0.0, 0.0] ],
                       coords_are_cartesian=False)
incarparams = {'System':'test',
               'ENCUT': 400,
               'ISMEAR': 1,
               'SIGMA': 0.1,
               'EDIFF':1E-6 }
incar = Incar(params=incarparams)
poscar = Poscar(structure, comment='Pt', selective_dynamics=None)
potcar = Potcar(symbols = poscar.site_symbols, 
                functional='PBE',
                sym_potcar_map=None)
kpoints = Kpoints(kpts=((8, 8, 8),))
turn_knobs = { 'ENCUT' : range(400, 500, 100),
               'KPOINTS': [k for k in range(20, 30, 10)]
             }
job_dir = 'calBulk'
qparams= dict(nnodes='1', ppnode='16', 
              job_name='vasp_job', pmem='1000mb',
              walltime='24:00:00',
              rocket_launch='mpirun /home/km468/Software/VASP/vasp.5.3.5/vasp')
qadapter = CommonAdapter(q_type="PBS",**qparams)
cal = Calibrate(incar, poscar, potcar, kpoints,
                turn_knobs = turn_knobs,
                qadapter = qadapter,
                job_dir = job_dir)
caltask = MPINTCalibrateTask(cal.as_dict())

#firework with launch directory set to $FW_JOB_DIR, an environment variable
#spec={'_launch_dir':'$FW_JOB_DIR'}, 
fw_calibrate = Firework([caltask], 
                        name="fw_test")
wf = Workflow([fw_calibrate], name="mpint_wf_test")
lp = LaunchPad.from_file(LAUNCHPAD_LOC)
print('fireworks in the database before adding the workflow: \n',
      lp.get_fw_ids())
lp.add_wf(wf)
print('fireworks in the database: \n', lp.get_fw_ids())

