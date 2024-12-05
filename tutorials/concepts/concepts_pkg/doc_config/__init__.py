from .coquantity.coquantity_eng import load_coqn_config
from .invoice.invoice_eng import load_invoice_config
from .bol.bol_eng import load_bol_config
from .coo.coo_eng import load_coo_config

coqn_config = load_coqn_config() 

invoice_config = load_invoice_config()

bol_config=load_bol_config()

coo_config=load_coo_config()