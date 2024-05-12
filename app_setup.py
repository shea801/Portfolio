import os, pkg_resources, subprocess, sys

# install the necessary modules and libraries to run python application
# create set of needed libraries and modules for the app
apps = {'dash',
        'numpy',
        'pandas',
        'plotly',
        'dash_bootstrap_components'
       }

# use pkg_resources module to verify modules that are already present
# and if not, install them...
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = apps - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing],
                         stdout=subprocess.DEVNULL)
    print(f"{missing} is installed for application use.")
