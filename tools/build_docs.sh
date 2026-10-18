#!/bin/sh
# Build the user guide into src/mbstudio/resources/ and copy the equations
# reference (the two-level model document of mbsolver) next to it.
# Expects the mbsolver repository next to this one (../mbsolver), or its path in
# MBSOLVER_DIR. Run from anywhere: sh tools/build_docs.sh
set -e
root="$(cd "$(dirname "$0")/.." && pwd)"
mbsolver="${MBSOLVER_DIR:-$root/../mbsolver}"
eqs="$mbsolver/docs/two_level.pdf"
if [ ! -f "$eqs" ]; then
    echo "Equations reference not found: $eqs" >&2
    echo "Clone https://github.com/vahid-anari/mbsolver next to this repository or set MBSOLVER_DIR." >&2
    exit 1
fi

cd "$root/docs"
version=$(sed -n 's/^version = "\(.*\)"/\1/p' "$root/pyproject.toml")
printf '\\newcommand{\\AppVersion}{%s}\n' "$version" > version.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build user_guide.tex

cp build/user_guide.pdf "$root/src/mbstudio/resources/user_guide.pdf"
cp "$eqs" "$root/src/mbstudio/resources/equations_reference.pdf"
echo "Built version $version into src/mbstudio/resources/ (equations reference from $mbsolver)"
