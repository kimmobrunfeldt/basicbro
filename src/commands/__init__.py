import os

this_path = os.path.realpath(__file__) # __init__.py current realpath
this_dir = os.path.dirname(this_path) # __init__.py current realdir

__all__ = []

for module in os.listdir(this_dir): # List files in this directory

    # Skip others than *.py files
    if module == '__init__.py' or module[-3:] != '.py':
        continue
        
    __import__(module[:-3], locals(), globals()) # import module
    __all__.append(module[:-3]) # add module to __all__
    
del module

