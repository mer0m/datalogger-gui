from os import listdir
from os.path import dirname

for module in listdir(dirname(__file__)):
	if module == '__init__.py' or module == 'abstract_instrument.py' or module[-3:] != '.py':
		continue
	__import__(module[:-3], locals(), globals())

del module, listdir, dirname