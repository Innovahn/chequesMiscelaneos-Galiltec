# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import locale
import pytz
from openerp.tools.translate import _

class account_journal(osv.osv):




	#asociate to the default journal sequence, the secuence for checks thaht is defined in the journal sequences 
	#this function will run when multisequence is defined
	def onchange_multy_currency(self, cr, uid,ids, allow_multi_sequence, context=None):
		res={}
		if allow_multi_sequence:
			for journal in self.browse(cr,uid,ids,context=None):
				if journal.sequence_ids:
					for seqs in journal.sequence_ids:
						if seqs.code=='check' :
							self.write(cr,uid,ids,{'sequence_id':seqs.id},context=context)
							return { 'value' : {'sequence_id' : seqs.id} }
							
		else:	
			return False
	
	_inherit = 'account.journal'
	_columns = {
		'checkmiscelaneous':fields.boolean(string="Miscellaneous Checks"),
		'allow_creditdebit':fields.boolean(string="Allow debit and credit"),
		'allow_deposits':fields.boolean(string="Allow deposits"),
		'allow_multi_sequence':fields.boolean(string="Allow Multi-Sequence"),
		'sequence_ids':fields.one2many('ir.sequence','journal_id',string='Sequences'),
		'commission_account' : fields.many2one('account.account',string='Commission account'),	
	}
	_defaults = {
	'checkmiscelaneous' : False,
	'allow_creditdebit' : False,
	'allow_multi_sequence' : False,
		} 
