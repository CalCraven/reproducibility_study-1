"""Initialize signac statepoints."""

import itertools
import os

import numpy as np
import signac
import unyt as u
from numpy import ModuleDeprecationWarning


def dict_product(dd):
    """Return the product of the key/values of a dictionary."""
    keys = dd.keys()
    for element in itertools.product(*dd.values()):
        yield dict(zip(keys, element))


molecules = ["waterSPCE", "waterSPCE_lammps"]
replicas = range(16)
simulation_engines = [
    "gromacs",
    "lammps-VU",
]
md_engines = ["gromacs", "hoomd", "lammps-VU"]
mc_engines = ["cassandra", "mcccs", "gomc"]
forcefields = {}
r_cuts = {}
cutoff_styles = ["hard"]
long_range_correction = ["energy_pressure"]
for key in molecules:
    if "UA" in key:
        if "benz" not in key:
            forcefields[key] = "trappe-ua"
        else:
            forcefields[key] = "benzene-ua"
        r_cuts[key] = 14.0 * u.angstrom
    elif "SPCE" in key:
        if "lammps" in key:
            forcefields[key] = "spce_lammps"
        else:
            forcefields[key] = "spce_original"
        r_cuts[key] = 9 * u.angstrom
    else:
        forcefields[key] = "oplsaa"
        r_cuts[key] = 10 * u.angstrom
g_per_cm3 = u.g / (u.cm * u.cm * u.cm)
masses = {
    "waterSPCE": [18.015324] * u.amu,
}
init_density_liq = {
    "waterSPCE": [0.998] * g_per_cm3,
}
init_density_vap = {
    "waterSPCE": [None],
}
temperatures = {
    "waterSPCE": [280.0, 300.0, 320.0] * u.K,
}

pressures = {
    "waterSPCE": [101.325, 101.325, 101.325] * u.kPa,
}

N_liq_molecules = {
    "waterSPCE": [1100, 1100, 1100],
}

N_vap_molecules = {
    "waterSPCE": [None],
}

liq_box_lengths = {
    "waterSPCE": [32.07] * u.angstrom,
}

vap_box_lengths = {
    "waterSPCE": [None],
}

ensembles = {
    "waterSPCE": ["NPT"],
}


pr_root = os.path.join(os.getcwd(), "src")
pr = signac.get_project(pr_root)

# ignore statepoints that are not being tested (gemc only for methane, pentane)
# filter the list of dictionaries
total_statepoints = list()
for molecule in molecules:
    if molecule == "waterSPCE_lammps":
        ff_for_molecule = molecule
        molecule = "waterSPCE"
    else:
        ff_for_molecule = molecule
    for (
        engine,
        ensemble,
        (temp, press),
        n_liq,
        liq_box_L,
        n_vap,
        vap_box_L,
        (init_liq_den, init_vap_den),
        mass,
        lrc,
        cutoff_style,
        replica,
    ) in itertools.product(
        simulation_engines,
        ensembles[molecule],
        zip(temperatures[molecule], pressures[molecule]),
        N_liq_molecules[molecule],
        liq_box_lengths[molecule],
        N_vap_molecules[molecule],
        vap_box_lengths[molecule],
        zip(init_density_liq[molecule], init_density_vap[molecule]),
        masses[molecule],
        long_range_correction,
        cutoff_styles,
        replicas,
    ):
        statepoint = {
            "molecule": molecule,
            "engine": engine,
            "replica": replica,
            "temperature": np.round(
                temp.to_value("K"),
                decimals=3,
            ).item(),
            "pressure": np.round(press.to_value("kPa"), decimals=3).item(),
            "ensemble": ensemble if ensemble else None,
            "N_liquid": n_liq,
            "N_vap": n_vap if n_vap else None,
            "box_L_liq": (
                np.round(
                    liq_box_L.to_value("nm"),
                    decimals=3,
                ).item()
                if liq_box_L
                else None
            ),
            "box_L_vap": (
                np.round(
                    vap_box_L.to_value("nm"),
                    decimals=3,
                ).item()
                if vap_box_L
                else None
            ),
            "init_liq_den": np.round(
                init_liq_den.to_value(g_per_cm3),
                decimals=3,
            ).item(),
            "init_vap_den": (
                np.round(
                    init_vap_den.to_value(g_per_cm3),
                    decimals=3,
                ).item()
                if init_vap_den
                else None
            ),
            "mass": np.round(
                mass.to_value("amu"),
                decimals=3,
            ).item(),
            "forcefield_name": forcefields[ff_for_molecule],
            "cutoff_style": cutoff_style,
            "long_range_correction": lrc,
            "r_cut": np.round(
                r_cuts[molecule].to_value("nm"),
                decimals=3,
            ).item(),
        }
        total_statepoints.append(statepoint)

indices_to_remove = set()
for i, sp in enumerate(total_statepoints):
    if sp["forcefield_name"] == "spce_lammps":
        if sp["temperature"] in [280, 320]:
            indices_to_remove.add(i)


# now reverse sort the set and remove from inital list
# must be reverse sorted to remove indices on the list in place
# otherwise the list will change size and the indices would change
# print(len(indices_to_remove))
sorted_indicies_to_delete = sorted(list(indices_to_remove), reverse=True)
for idx in sorted_indicies_to_delete:
    del total_statepoints[idx]

for sp in total_statepoints:
    pr.open_job(
        statepoint=sp,
    ).init()
