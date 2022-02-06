set -e
echo "Clean up"
rm -f TOC.md
rm -Rf fermions
rm -Rf bosons

echo "Prepare"
cp template.md TOC.md
python tocer.py TOC.md

echo "Testing"
for EXPECTED_FILE in fermions/TOC.md fermions/leptons/TOC.md fermions/leptons/electron.md fermions/leptons/electron-neutrino.md fermions/quarks/TOC.md fermions/quarks/bottom.md
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

if [ ! -z "$(cat TOC.md | grep "* \[Quarks](fermions/quarks/TOC.md)")" ]
then
    echo "[PASS] quarks link valid"
else
    echo "[FAIL] quarks link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[Bottom](fermions/quarks/bottom.md)")" ]
then
    echo "[PASS] bottom link valid"
else
    echo "[FAIL] bottom link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a](a/TOC.md)")" ]
then
    echo "[PASS] a link valid"
else
    echo "[FAIL] a link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.1](a/a-1/TOC.md)")" ]
then
    echo "[PASS] a.1 link valid"
else
    echo "[FAIL] a.1 link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.1.1](a/a-1/a-1-1/TOC.md)")" ]
then
    echo "[PASS] a.1.1 link valid"
else
    echo "[FAIL] a.1.1 link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.1.1.1](a/a-1/a-1-1/a-1-1-1.md)")" ]
then
    echo "[PASS] a.1.1 link valid"
else
    echo "[FAIL] a.1.1 link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.1.2](a/a-1/a-1-2.md)")" ]
then
    echo "[PASS] a.1.2 link valid"
else
    echo "[FAIL] a.1.2 link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.2](a/a-2/TOC.md)")" ]
then
    echo "[PASS] a.2 link valid"
else
    echo "[FAIL] a.2 link invalid"
fi

if [ ! -z "$(cat TOC.md | grep "* \[a.2.1](a/a-2/a-2-1.md)")" ]
then
    echo "[PASS] a.2.1 link valid"
else
    echo "[FAIL] a.2.1 link invalid"
fi



