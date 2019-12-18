#!/bin/bash -lc

echo "INSTALLING DEPENDENCIES"
pip install -U -I -r requirements_test.txt

echo "COMPILING TEMPLATE"
python -c "from boa.compiler import Compiler; Compiler.load_and_save('ico_template.py')"

echo "TEMPLATE SUCCESSFULLY COMPILED"
