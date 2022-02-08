from distutils.core import setup

import propellant

setup(
    name='propellant',
    version=propellant.__version__,
    description='Linux-agnostic autosetup script with an emphasis on configurability.',
    packages=['propellant', 'propellant.lib'],
    scripts=['propellant/__main__.py']
)
