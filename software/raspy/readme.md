### Script to be run on the Raspberry Pi

Currently development in this branch is focused on `detect_test.py`.  
`detect_test.py` gets called via the main entry point `../billardtrainer.py`, when flag `-pc` is set.
It then initializes a Camera, calibrates it and then runs detection on the input specified, using
the classes in `../classes`.

`main.py` is merged from master-branch.
