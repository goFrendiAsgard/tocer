set -e
echo "Clean up"
rm -f TOC.md
rm -Rf fermions
rm -Rf bosons

echo "Prepare"
cp template.md TOC.md
python tocer.py TOC.md

echo "Testing"
for EXPECTED_FILE in fermions/TOC.md fermions/leptons/TOC.md fermions/leptons/electron.md fermions/leptons/electron-neutrino.md
do
    if [ -f "${EXPECTED_FILE}" ]
    then
        echo "[PASS] ${EXPECTED_FILE} exists"
    else
        echo "[FAIL] ${EXPECTED_FILE} doesn't exist"
    fi
done

if [ ! -z "$(cat TOC.md | grep "* \[🧶 Fermions](fermions/TOC.md)")" ]
then
    echo "[PASS] Fermions link valid"
else
    echo "[FAIL] Fermions link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[Leptons](fermions/leptons/TOC.md)")" ]
then
    echo "[PASS] leptons link valid"
else
    echo "[FAIL] leptons link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[Electron](fermions/leptons/electron.md)")" ]
then
    echo "[PASS] electron link valid"
else
    echo "[FAIL] electron link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[Electron Neutrino](fermions/leptons/electron-neutrino.md)")" ]
then
    echo "[PASS] electron neutrino link valid"
else
    echo "[FAIL] electron neutrino link invalid"
fi

