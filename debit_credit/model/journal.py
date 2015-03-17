# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import locale
import pytz
from openerp.tools.translate import _



		
class account_journal(osv.osv):
	_inherit = 'account.journal'
	_columns = {
		'allow_creditdebit':fields.boolean(string="Allow debit and credit"),
		
	
	}
	_defaults = {
	'allow_creditdebit' : False,
	
		} 
