set -e
echo "Clean up"
rm -Rf testDir

echo "Prepare"
mkdir -p testDir
cp test-template.md testDir/README.md
cd testDir
python ../tocer.py README.md

echo "Testing"
for EXPECTED_FILE in fermions/README.md fermions/leptons/README.md fermions/leptons/electron.md fermions/leptons/electron-neutrino.md fermions/quarks/README.md fermions/quarks/bottom.md
do
    if [ -f "${EXPECTED_FILE}" ]
    then
        echo "[✅ PASS] ${EXPECTED_FILE} exists"
    else
        echo "[❌ FAIL] ${EXPECTED_FILE} doesn't exist"
    fi
done

if [ ! -z "$(cat README.md | grep "* \[🧶 Fermions](fermions/README\.md)")" ]
then
    echo "[✅ PASS] Fermions link valid"
else
    echo "[❌ FAIL] Fermions link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[Leptons](fermions/leptons/README\.md)")" ]
then
    echo "[✅ PASS] leptons link valid"
else
    echo "[❌ FAIL] leptons link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[Electron](fermions/leptons/electron\.md)")" ]
then
    echo "[✅ PASS] electron link valid"
else
    echo "[❌ FAIL] electron link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[Electron Neutrino](fermions/leptons/electron-neutrino\.md)")" ]
then
    echo "[✅ PASS] electron neutrino link valid"
else
    echo "[❌ FAIL] electron neutrino link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[Quarks](fermions/quarks/README\.md)")" ]
then
    echo "[✅ PASS] quarks link valid"
else
    echo "[❌ FAIL] quarks link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[Bottom](fermions/quarks/bottom\.md)")" ]
then
    echo "[✅ PASS] bottom link valid"
else
    echo "[❌ FAIL] bottom link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a](a/README\.md)")" ]
then
    echo "[✅ PASS] a link valid"
else
    echo "[❌ FAIL] a link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.1](a/a-1/README\.md)")" ]
then
    echo "[✅ PASS] a.1 link valid"
else
    echo "[❌ FAIL] a.1 link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.1.1](a/a-1/a-1-1/README\.md)")" ]
then
    echo "[✅ PASS] a.1.1 link valid"
else
    echo "[❌ FAIL] a.1.1 link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.1.1.1](a/a-1/a-1-1/a-1-1-1\.md)")" ]
then
    echo "[✅ PASS] a.1.1 link valid"
else
    echo "[❌ FAIL] a.1.1 link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.1.2](a/a-1/a-1-2\.md)")" ]
then
    echo "[✅ PASS] a.1.2 link valid"
else
    echo "[❌ FAIL] a.1.2 link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.2](a/a-2/README\.md)")" ]
then
    echo "[✅ PASS] a.2 link valid"
else
    echo "[❌ FAIL] a.2 link invalid"
fi

if [ ! -z "$(cat README.md | grep "* \[a.2.1](a/a-2/a-2-1\.md)")" ]
then
    echo "[✅ PASS] a.2.1 link valid"
else
    echo "[❌ FAIL] a.2.1 link invalid"
fi


if [ ! -z "$(cat README.md | grep "\├\─\─ README\.md")" ]
then
    echo "[✅ PASS] code executed"
else
    echo "[❌ FAIL] code not executed"
fi
