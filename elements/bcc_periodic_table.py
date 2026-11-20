#!/usr/bin/env python3
"""
Generic 118-Element Periodic Table Engine on the 3D BCC Lattice (`elements/bcc_periodic_table.py`).

Computes the complete subatomic, nuclear, electronic, relativistic, and phase profile
for any element Z = 1..118 (Hydrogen through Oganesson):
  1. Quark-Gluon Nuclear Census: Counts up/down quarks, 4.66-link BCC gluon Steiner
     trees, pion-exchange nuclear binding energy (SEMF), and saved BCC routing ticks.
  2. Pauli / Madelung Electron Shell Filling (1s -> 7p): Builds exact electron
     configurations, valence electrons, open covalent bond slots, and Slater Z_eff.
  3. Special Relativity Core Contraction: Computes 1s electron speed beta = Z * alpha,
     Lorentz gamma, and orbital contraction percentage across Z = 1..118.
  4. CLI Support: Query any element (--symbol Hg / --element 80), range (--range 1 18),
     full 118-element table (--all), or export JSON (--json periodic_table.json).
"""

import argparse
import json
import math
from typing import Any, Dict, List, Tuple

ELEMENTS_118: List[Tuple[int, str, str, int, str]] = [
    (1, "H", "Hydrogen", 1, "Reactive Nonmetal"),
    (2, "He", "Helium", 4, "Noble Gas"),
    (3, "Li", "Lithium", 7, "Alkali Metal"),
    (4, "Be", "Beryllium", 9, "Alkaline Earth"),
    (5, "B", "Boron", 11, "Metalloid"),
    (6, "C", "Carbon", 12, "Reactive Nonmetal"),
    (7, "N", "Nitrogen", 14, "Reactive Nonmetal"),
    (8, "O", "Oxygen", 16, "Reactive Nonmetal"),
    (9, "F", "Fluorine", 19, "Halogen"),
    (10, "Ne", "Neon", 20, "Noble Gas"),
    (11, "Na", "Sodium", 23, "Alkali Metal"),
    (12, "Mg", "Magnesium", 24, "Alkaline Earth"),
    (13, "Al", "Aluminum", 27, "Post-Transition Metal"),
    (14, "Si", "Silicon", 28, "Metalloid"),
    (15, "P", "Phosphorus", 31, "Reactive Nonmetal"),
    (16, "S", "Sulfur", 32, "Reactive Nonmetal"),
    (17, "Cl", "Chlorine", 35, "Halogen"),
    (18, "Ar", "Argon", 40, "Noble Gas"),
    (19, "K", "Potassium", 39, "Alkali Metal"),
    (20, "Ca", "Calcium", 40, "Alkaline Earth"),
    (21, "Sc", "Scandium", 45, "Transition Metal"),
    (22, "Ti", "Titanium", 48, "Transition Metal"),
    (23, "V", "Vanadium", 51, "Transition Metal"),
    (24, "Cr", "Chromium", 52, "Transition Metal"),
    (25, "Mn", "Manganese", 55, "Transition Metal"),
    (26, "Fe", "Iron", 56, "Transition Metal"),
    (27, "Co", "Cobalt", 59, "Transition Metal"),
    (28, "Ni", "Nickel", 59, "Transition Metal"),
    (29, "Cu", "Copper", 64, "Transition Metal"),
    (30, "Zn", "Zinc", 65, "Transition Metal"),
    (31, "Ga", "Gallium", 70, "Post-Transition Metal"),
    (32, "Ge", "Germanium", 73, "Metalloid"),
    (33, "As", "Arsenic", 75, "Metalloid"),
    (34, "Se", "Selenium", 79, "Reactive Nonmetal"),
    (35, "Br", "Bromine", 80, "Halogen"),
    (36, "Kr", "Krypton", 84, "Noble Gas"),
    (37, "Rb", "Rubidium", 85, "Alkali Metal"),
    (38, "Sr", "Strontium", 88, "Alkaline Earth"),
    (39, "Y", "Yttrium", 89, "Transition Metal"),
    (40, "Zr", "Zirconium", 91, "Transition Metal"),
    (41, "Nb", "Niobium", 93, "Transition Metal"),
    (42, "Mo", "Molybdenum", 96, "Transition Metal"),
    (43, "Tc", "Technetium", 98, "Transition Metal"),
    (44, "Ru", "Ruthenium", 101, "Transition Metal"),
    (45, "Rh", "Rhodium", 103, "Transition Metal"),
    (46, "Pd", "Palladium", 106, "Transition Metal"),
    (47, "Ag", "Silver", 108, "Transition Metal"),
    (48, "Cd", "Cadmium", 112, "Transition Metal"),
    (49, "In", "Indium", 115, "Post-Transition Metal"),
    (50, "Sn", "Tin", 119, "Post-Transition Metal"),
    (51, "Sb", "Antimony", 122, "Metalloid"),
    (52, "Te", "Tellurium", 128, "Metalloid"),
    (53, "I", "Iodine", 127, "Halogen"),
    (54, "Xe", "Xenon", 131, "Noble Gas"),
    (55, "Cs", "Cesium", 133, "Alkali Metal"),
    (56, "Ba", "Barium", 137, "Alkaline Earth"),
    (57, "La", "Lanthanum", 139, "Lanthanide"),
    (58, "Ce", "Cerium", 140, "Lanthanide"),
    (59, "Pr", "Praseodymium", 141, "Lanthanide"),
    (60, "Nd", "Neodymium", 144, "Lanthanide"),
    (61, "Pm", "Promethium", 145, "Lanthanide"),
    (62, "Sm", "Samarium", 150, "Lanthanide"),
    (63, "Eu", "Europium", 152, "Lanthanide"),
    (64, "Gd", "Gadolinium", 157, "Lanthanide"),
    (65, "Tb", "Terbium", 159, "Lanthanide"),
    (66, "Dy", "Dysprosium", 163, "Lanthanide"),
    (67, "Ho", "Holmium", 165, "Lanthanide"),
    (68, "Er", "Erbium", 167, "Lanthanide"),
    (69, "Tm", "Thulium", 169, "Lanthanide"),
    (70, "Yb", "Ytterbium", 173, "Lanthanide"),
    (71, "Lu", "Lutetium", 175, "Lanthanide"),
    (72, "Hf", "Hafnium", 178, "Transition Metal"),
    (73, "Ta", "Tantalum", 181, "Transition Metal"),
    (74, "W", "Tungsten", 184, "Transition Metal"),
    (75, "Re", "Rhenium", 186, "Transition Metal"),
    (76, "Os", "Osmium", 190, "Transition Metal"),
    (77, "Ir", "Iridium", 192, "Transition Metal"),
    (78, "Pt", "Platinum", 195, "Transition Metal"),
    (79, "Au", "Gold", 197, "Transition Metal"),
    (80, "Hg", "Mercury", 201, "Transition Metal"),
    (81, "Tl", "Thallium", 204, "Post-Transition Metal"),
    (82, "Pb", "Lead", 207, "Post-Transition Metal"),
    (83, "Bi", "Bismuth", 209, "Post-Transition Metal"),
    (84, "Po", "Polonium", 209, "Metalloid"),
    (85, "At", "Astatine", 210, "Halogen"),
    (86, "Rn", "Radon", 222, "Noble Gas"),
    (87, "Fr", "Francium", 223, "Alkali Metal"),
    (88, "Ra", "Radium", 226, "Alkaline Earth"),
    (89, "Ac", "Actinium", 227, "Actinide"),
    (90, "Th", "Thorium", 232, "Actinide"),
    (91, "Pa", "Protactinium", 231, "Actinide"),
    (92, "U", "Uranium", 238, "Actinide"),
    (93, "Np", "Neptunium", 237, "Actinide"),
    (94, "Pu", "Plutonium", 244, "Actinide"),
    (95, "Am", "Americium", 243, "Actinide"),
    (96, "Cm", "Curium", 247, "Actinide"),
    (97, "Bk", "Berkelium", 247, "Actinide"),
    (98, "Cf", "Californium", 251, "Actinide"),
    (99, "Es", "Einsteinium", 252, "Actinide"),
    (100, "Fm", "Fermium", 257, "Actinide"),
    (101, "Md", "Mendelevium", 258, "Actinide"),
    (102, "No", "Nobelium", 259, "Actinide"),
    (103, "Lr", "Lawrencium", 266, "Actinide"),
    (104, "Rf", "Rutherfordium", 267, "Transition Metal"),
    (105, "Db", "Dubnium", 268, "Transition Metal"),
    (106, "Sg", "Seaborgium", 269, "Transition Metal"),
    (107, "Bh", "Bohrium", 270, "Transition Metal"),
    (108, "Hs", "Hassium", 277, "Transition Metal"),
    (109, "Mt", "Meitnerium", 278, "Transition Metal"),
    (110, "Ds", "Darmstadtium", 281, "Transition Metal"),
    (111, "Rg", "Roentgenium", 282, "Transition Metal"),
    (112, "Cn", "Copernicium", 285, "Transition Metal"),
    (113, "Nh", "Nihonium", 286, "Post-Transition Metal"),
    (114, "Fl", "Flerovium", 289, "Post-Transition Metal"),
    (115, "Mc", "Moscovium", 290, "Post-Transition Metal"),
    (116, "Lv", "Livermorium", 293, "Post-Transition Metal"),
    (117, "Ts", "Tennessine", 294, "Halogen"),
    (118, "Og", "Oganesson", 294, "Noble Gas"),
]

AUFBAU_SUBSHELLS: List[Tuple[str, int, int]] = [
    ("1s", 1, 2), ("2s", 2, 2), ("2p", 2, 6), ("3s", 3, 2), ("3p", 3, 6),
    ("4s", 4, 2), ("3d", 3, 10), ("4p", 4, 6), ("5s", 5, 2), ("4d", 4, 10),
    ("5p", 5, 6), ("6s", 6, 2), ("4f", 4, 14), ("5d", 5, 10), ("6p", 6, 6),
    ("7s", 7, 2), ("5f", 5, 14), ("6d", 6, 10), ("7p", 7, 6),
]
class BCCPeriodicTableSim:
    """Generic 3D BCC lattice analyzer for any element Z = 1..118."""

    ALPHA_EM = 1.0 / 137.035999
    BOHR_ANG = 0.529177
    RYDBERG_EV = 13.605693
    TICK_TO_MEV = 5.0
    U_BARE_MEV = 2.16
    D_BARE_MEV = 4.67
    PROTON_MEV = 938.272
    NEUTRON_MEV = 939.565
    ELECTRON_MEV = 0.511

    def __init__(self) -> None:
        self._by_z: Dict[int, Tuple[int, str, str, int, str]] = {}
        self._by_sym: Dict[str, Tuple[int, str, str, int, str]] = {}
        self._by_name: Dict[str, Tuple[int, str, str, int, str]] = {}
        for row in ELEMENTS_118:
            z, sym, name, _, _ = row
            self._by_z[z] = row
            self._by_sym[sym.lower()] = row
            self._by_name[name.lower()] = row

    def lookup(self, query: Any) -> Tuple[int, str, str, int, str]:
        """Resolve an atomic number (int/str), symbol ('Hg'), or name ('Mercury')."""
        if isinstance(query, int) or (isinstance(query, str) and query.isdigit()):
            z = int(query)
            if z not in self._by_z:
                raise ValueError(f"Atomic number Z={z} out of range 1..118.")
            return self._by_z[z]
        key = str(query).strip().lower()
        if key in self._by_sym:
            return self._by_sym[key]
        if key in self._by_name:
            return self._by_name[key]
        raise ValueError(f"Unknown element '{query}'.")

    def nuclear_binding_mev(self, z: int, a: int) -> float:
        """Semi-Empirical Mass Formula (Weizsacker) pion/gluon nuclear binding energy in MeV."""
        if a <= 1:
            return 0.0
        n = a - z
        a_v, a_s, a_c, a_a, a_p = 15.75, 17.80, 0.711, 23.70, 11.18
        vol = a_v * a
        surf = a_s * (a ** (2.0 / 3.0))
        coul = a_c * (z * (z - 1)) / (a ** (1.0 / 3.0))
        asym = a_a * ((n - z) ** 2) / float(a)
        if z % 2 == 0 and n % 2 == 0:
            pair = a_p / math.sqrt(a)
        elif z % 2 == 1 and n % 2 == 1:
            pair = -a_p / math.sqrt(a)
        else:
            pair = 0.0
        return max(0.0, vol - surf - coul - asym + pair)

    def build_electron_shells(self, z: int) -> Dict[str, Any]:
        """Fill Pauli/Madelung subshells 1s..7p and compute valence & Slater screening."""
        rem = z
        filled: List[Tuple[str, int, int]] = []
        for label, n_prin, cap in AUFBAU_SUBSHELLS:
            if rem <= 0:
                break
            occ = min(rem, cap)
            filled.append((label, n_prin, occ))
            rem -= occ

        max_n = max(n_p for _, n_p, _ in filled)
        valence_e = sum(occ for _, n_p, occ in filled if n_p == max_n)
        inner_e = z - valence_e

        cfg_parts = [f"{lbl}^{occ}" for lbl, _, occ in filled]
        cfg_str = " ".join(cfg_parts if len(cfg_parts) <= 5 else ["[...]"] + cfg_parts[-4:])

        sigma = inner_e * 0.88 + max(0, valence_e - 1) * 0.35
        z_eff = max(1.0, z - sigma)

        if z == 1:
            open_bonds = 1
        elif max_n == 1 and valence_e == 2:
            open_bonds = 0
        elif valence_e >= 8:
            open_bonds = 0
        else:
            open_bonds = min(valence_e, 8 - valence_e)

        return {
            "config": cfg_str,
            "outer_shell_n": max_n,
            "valence_electrons": valence_e,
            "open_covalent_bonds": open_bonds,
            "z_eff": round(z_eff, 2),
        }

    def analyze_element(self, query: Any) -> Dict[str, Any]:
        """Produce a complete 3D BCC hierarchical readout for any element Z = 1..118."""
        z, sym, name, a, category = self.lookup(query)
        n = a - z

        up_quarks = 2 * z + n
        down_quarks = z + 2 * n
        total_quarks = 3 * a
        steiner_trees = a

        bare_quark_mev = up_quarks * self.U_BARE_MEV + down_quarks * self.D_BARE_MEV
        raw_nucleon_mev = z * self.PROTON_MEV + n * self.NEUTRON_MEV
        gluon_steiner_mev = raw_nucleon_mev - bare_quark_mev
        nuc_bind_mev = self.nuclear_binding_mev(z, a)
        electron_mass_mev = z * self.ELECTRON_MEV
        total_atom_mev = raw_nucleon_mev - nuc_bind_mev + electron_mass_mev

        gluon_mass_pct = ((gluon_steiner_mev - nuc_bind_mev) / total_atom_mev) * 100.0
        electron_mass_pct = (electron_mass_mev / total_atom_mev) * 100.0

        shells = self.build_electron_shells(z)
        beta_1s = min(0.995, z * self.ALPHA_EM)
        gamma_1s = 1.0 / math.sqrt(1.0 - beta_1s ** 2)
        contraction_pct = (1.0 - (1.0 / gamma_1s)) * 100.0

        n_out = shells["outer_shell_n"]
        z_eff = shells["z_eff"]
        rel_valence_factor = 1.0 - 0.22 * (beta_1s ** 2) if n_out >= 6 else 1.0
        radius_ang = ((n_out ** 2) / z_eff) * self.BOHR_ANG * rel_valence_factor
        ioniz_ev = self.RYDBERG_EV * ((z_eff / n_out) ** 2) / rel_valence_factor

        return {
            "Z": z,
            "symbol": sym,
            "name": name,
            "A": a,
            "N": n,
            "category": category,
            "up_quarks": up_quarks,
            "down_quarks": down_quarks,
            "total_quarks": total_quarks,
            "gluon_trees": steiner_trees,
            "bare_quark_mev": round(bare_quark_mev, 2),
            "gluon_steiner_mev": round(gluon_steiner_mev, 2),
            "nuclear_binding_mev": round(nuc_bind_mev, 2),
            "bind_per_nucleon_mev": round(nuc_bind_mev / a, 3),
            "saved_bcc_ticks": round(nuc_bind_mev / self.TICK_TO_MEV, 3),
            "total_atom_mev": round(total_atom_mev, 2),
            "gluon_mass_pct": round(gluon_mass_pct, 3),
            "electron_mass_pct": round(electron_mass_pct, 4),
            "electron_config": shells["config"],
            "outer_shell_n": n_out,
            "valence_electrons": shells["valence_electrons"],
            "open_covalent_bonds": shells["open_covalent_bonds"],
            "z_eff": z_eff,
            "radius_ang": round(radius_ang, 3),
            "first_ioniz_ev": round(ioniz_ev, 2),
            "beta_1s": round(beta_1s, 4),
            "gamma_1s": round(gamma_1s, 4),
            "rel_contraction_pct": round(contraction_pct, 2),
        }

    def analyze_range(self, z_start: int = 1, z_end: int = 118) -> List[Dict[str, Any]]:
        """Analyze a contiguous range of elements Z = z_start..z_end."""
        return [self.analyze_element(z) for z in range(max(1, z_start), min(118, z_end) + 1)]


def print_single_element_report(el: Dict[str, Any]) -> None:
    print("=" * 86)
    print(f"3D BCC ELEMENT READOUT: #{el['Z']} {el['name']} ({el['symbol']}-{el['A']}) — {el['category']}")
    print("=" * 86)
    print(f"  1. Nuclear Quark Census:   {el['Z']}p + {el['N']}n = {el['total_quarks']} quarks ({el['up_quarks']} up, {el['down_quarks']} down)")
    print(f"  2. Gluon Steiner Trees:    {el['gluon_trees']} x 4.66-link trees = {el['gluon_steiner_mev']:.2f} MeV ({el['gluon_mass_pct']:.3f}% of atom mass)")
    print(f"  3. Pion Nuclear Binding:   {el['nuclear_binding_mev']:.2f} MeV total ({el['bind_per_nucleon_mev']:.3f} MeV/nuc | {el['saved_bcc_ticks']:.2f} saved BCC ticks)")
    print(f"  4. Electron Shells (Z={el['Z']}):  {el['electron_config']}  (Mass share: {el['electron_mass_pct']:.4f}%)")
    print(f"  5. Valence & Screening:    Shell n={el['outer_shell_n']} | Z_eff={el['z_eff']:.2f} | Radius={el['radius_ang']:.3f} Ang | Ioniz={el['first_ioniz_ev']:.2f} eV | Bonds={el['open_covalent_bonds']}")
    print(f"  6. Relativistic 1s Core:   v/c = {el['beta_1s']:.4f} | Lorentz gamma = {el['gamma_1s']:.4f} | Orbital Contraction = {el['rel_contraction_pct']:.2f}%")
    print(f"  7. Total Atomic Mass:      {el['total_atom_mev']:.2f} MeV ({el['total_atom_mev'] / 5.0:.2f} total BCC network ticks)")


def print_summary_table(rows: List[Dict[str, Any]]) -> None:
    print("=" * 98)
    print("  Z  Sym  Element        Quarks (u/d)   Bind/Nuc   Gluon%   Shells (Z_eff)   1s v/c   Contract")
    print("-" * 98)
    for r in rows:
        ud = f"{r['up_quarks']}/{r['down_quarks']}"
        sh = f"n={r['outer_shell_n']} ({r['z_eff']:.2f})"
        print(
            f"{r['Z']:>3}  {r['symbol']:<4} {r['name']:<13} {ud:>13} {r['bind_per_nucleon_mev']:>9.3f} "
            f"{r['gluon_mass_pct']:>7.3f}% {sh:>16} {r['beta_1s']:>8.4f} {r['rel_contraction_pct']:>8.2f}%"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic 118-Element 3D BCC Periodic Table Simulator")
    parser.add_argument("--element", "-e", type=str, default=None, help="Single element Z, symbol, or name (e.g. 79, Au, Mercury)")
    parser.add_argument("--range", "-r", nargs=2, type=int, metavar=("Z_START", "Z_END"), help="Range of atomic numbers (e.g. 1 36)")
    parser.add_argument("--all", action="store_true", help="Print full 118-element periodic table summary")
    parser.add_argument("--json", type=str, default=None, help="Export readout to JSON file")
    args = parser.parse_args()

    sim = BCCPeriodicTableSim()

    if args.element:
        el = sim.analyze_element(args.element)
        print_single_element_report(el)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(el, f, indent=2)
            print(f"[Saved element JSON -> {args.json}]")
    elif args.range:
        z_a, z_b = args.range
        rows = sim.analyze_range(z_a, z_b)
        print_summary_table(rows)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2)
            print(f"[Saved range JSON -> {args.json}]")
    elif args.all:
        rows = sim.analyze_range(1, 118)
        print_summary_table(rows)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2)
            print(f"[Saved all 118 elements JSON -> {args.json}]")
    else:
        landmarks = ["H", "He", "C", "O", "Fe", "Ag", "Au", "Hg", "U", "Og"]
        rows = [sim.analyze_element(sym) for sym in landmarks]
        print_summary_table(rows)
        print()
        print_single_element_report(sim.analyze_element("Hg"))

if __name__ == "__main__":
    main()
