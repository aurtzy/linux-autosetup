
build:
	pex -o propellant.pex --python-shebang='/usr/bin/env python3' -D . -r requirements.txt -e propellant
