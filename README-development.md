# Working on druid
This readme is meant for those who want to work on druid itself.

## Setup
First create a [virtual environment](https://docs.python.org/3/library/venv.html) and then do an [editable install](https://pip.pypa.io/en/latest/reference/pip_install/#editable-installs) of druid.
```
cd <directory where druid is checked out>
# Create virtual environment
python3 -m venv .venv
# Active the virtual environment
source .venv/bin/activate
# Do an editable install of druid
pip install -e .
# Activate the virtual environment again to add the druid that's now installed in the virtual environment to $PATH
source .venv/bin/activate
# Now execute druid, which runs directly from the code from this directory
druid
```

Closing the terminal will also exit the virtual environment. Running `deactivate` will exit the virtual environment as well.

If at a later point you want to start working on druid again it's enough to activate the virtual environment again using
```
cd <directory where druid is checked out>
source .venv/bin/activate
druid
```
