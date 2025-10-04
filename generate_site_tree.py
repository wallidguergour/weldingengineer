#!/usr/bin/env python3
"""
generate_site_tree.py
---------------------
Generate a bilingual (EN at root, FR under /fr/) directory structure for a documentation website.
- Cross-platform (Windows/macOS/Linux)
- Creates `.gitkeep` files in each leaf directory by default
- Idempotent: safe to re-run

Usage:
  python generate_site_tree.py --base /path/to/your/site/root
  python generate_site_tree.py --no-gitkeep
"""
from pathlib import Path
import argparse
import sys

EN_PATHS = [
    # Guides
    "guides/mig/introduction/",
    "guides/mig/settings/",
    "guides/mig/common-defects/",
    "guides/tig/stainless-steel/",
    "guides/tig/aluminium/",
    "guides/tig/titanium/",
    "guides/fcaw/basics/",
    "guides/fcaw/multi-pass/",
    "guides/fcaw/parameters/",
    "guides/smaw/introduction/",
    "guides/smaw/advanced-techniques/",
    "guides/metallurgy/heat-affected-zone/",
    "guides/metallurgy/stress-deformation/",
    "guides/metallurgy/heat-treatment/",
    "guides/qa-qc/visual-inspection/",
    "guides/qa-qc/ndt-tests/",
    "guides/qa-qc/standards/",
    "guides/automation/python-wps/",
    "guides/automation/heat-input-calculator/",
    "guides/automation/report-generation/",
    # Articles
    "articles/standards/nasa-welding/",
    "articles/standards/aws-d1-1/",
    "articles/standards/iso-9606/",
    "articles/industry/mining-australia/",
    "articles/industry/aerospace-welding/",
    "articles/industry/shipbuilding/",
    "articles/career/salaries-canada/",
    "articles/career/salaries-australia/",
    "articles/career/freelance-welder/",
    "articles/innovation/robotics/",
    "articles/innovation/metal-3d-printing/",
    "articles/innovation/new-consumables/",
    # Tools
    "tools/heat-input-simulator/",
    "tools/bead-profile/",
    "tools/plate-deformation/",
    "tools/wps-calculator/",
    # Singles
    "downloads/",
    "about/",
    "contact/",
    "search/",
]

FR_PATHS = [
    # Guides
    "fr/guides/mig/introduction/",
    "fr/guides/mig/reglages/",
    "fr/guides/mig/defauts-courants/",
    "fr/guides/tig/acier-inox/",
    "fr/guides/tig/aluminium/",
    "fr/guides/tig/titane/",
    "fr/guides/fcaw/bases/",
    "fr/guides/fcaw/multi-passes/",
    "fr/guides/fcaw/parametres/",
    "fr/guides/smaw/introduction/",
    "fr/guides/smaw/techniques-avancees/",
    "fr/guides/metallurgie/zone-affectee-thermiquement/",
    "fr/guides/metallurgie/contraintes-deformation/",
    "fr/guides/metallurgie/traitements-thermiques/",
    "fr/guides/qa-qc/inspection-visuelle/",
    "fr/guides/qa-qc/essais-non-destructifs/",
    "fr/guides/qa-qc/normes/",
    "fr/guides/automation/python-wps/",
    "fr/guides/automation/calcul-apport-thermique/",
    "fr/guides/automation/generation-rapports/",
    # Articles
    "fr/articles/standards/nasa-soudage/",
    "fr/articles/standards/aws-d1-1/",
    "fr/articles/standards/iso-9606/",
    "fr/articles/industrie/minier-australie/",
    "fr/articles/industrie/soudage-aerospatial/",
    "fr/articles/industrie/naval/",
    "fr/articles/carriere/salaires-canada/",
    "fr/articles/carriere/salaires-australie/",
    "fr/articles/carriere/devenir-soudeur-independant/",
    "fr/articles/innovation/robotique/",
    "fr/articles/innovation/impression-3d-metal/",
    "fr/articles/innovation/nouveaux-consommables/",
    # Outils
    "fr/outils/simulateur-apport-thermique/",
    "fr/outils/profil-cordon/",
    "fr/outils/deformation-toles/",
    "fr/outils/calcul-wps/",
    # Singles
    "fr/downloads/",
    "fr/a-propos/",
    "fr/contact/",
    "fr/recherche/",
]

def create_dirs(base: Path, rel_paths, make_gitkeep: bool=True) -> int:
    created = 0
    for rel in rel_paths:
        d = (base / rel).resolve()
        d.mkdir(parents=True, exist_ok=True)
        created += 1
        # Place a .gitkeep in the deepest directory to keep it in VCS
        if make_gitkeep:
            keep = d / ".gitkeep"
            if not keep.exists():
                keep.write_text("")
    return created

def main():
    parser = argparse.ArgumentParser(description="Generate bilingual site directory structure (EN at root, FR under /fr/).")
    parser.add_argument("--base", type=str, default=".", help="Base path where the tree will be created (default: current directory).")
    parser.add_argument("--no-gitkeep", action="store_true", help="Do not create .gitkeep files in directories.")
    args = parser.parse_args()

    base = Path(args.base).expanduser().resolve()
    base.mkdir(parents=True, exist_ok=True)

    make_gitkeep = not args.no_gitkeep

    en_count = create_dirs(base, EN_PATHS, make_gitkeep=make_gitkeep)
    fr_count = create_dirs(base, FR_PATHS, make_gitkeep=make_gitkeep)

    print(f"✅ Created/ensured {en_count} EN directories and {fr_count} FR directories under: {base}")
    if make_gitkeep:
        print("• `.gitkeep` files added to leaf directories.")
    else:
        print("• Skipped `.gitkeep` creation.")

if __name__ == "__main__":
    sys.exit(main())
