# Questo file è intenzionalmente vuoto.
# La sua presenza indica a Python che questa directory
# deve essere trattata come un "package" (un modulo che può contenere altri moduli).
#
# Questo permette di utilizzare importazioni relative (es. from . import models)
# all'interno del package e importazioni assolute (es. from src import services)
# da codice esterno al package.
from .translator import generate_sql_from_question