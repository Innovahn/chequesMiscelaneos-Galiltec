# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime

class account_journal(osv.Model):
	#asociate to the default journal sequence, the secuence for checks thaht is defined in the journal sequences 
	#this function will run when multisequence is defined
	def onchange_multy_currency(self, cr, uid,ids, allow_multi_sequence, context=None):
		if allow_multi_sequence:
			for journal in self.browse(cr,uid,ids,context=None):
				if journal.sequence_ids:
					for seqs in journal.sequence_ids:
						if seqs.code=='check' :
							self.write(cr,uid,ids,{'sequence_id':seqs.id},context=context)
							
		else:	
			return False


	
	_inherit = 'account.journal'
	_columns = {
		'allow_multi_sequence':fields.boolean(string="Allow Multi-Sequence"),
		'sequence_ids':fields.one2many('ir.sequence','journal_id',string='Sequences'),
		'commission_account' : fields.many2one('account.account',string='Commission account'),
		#'credit_debit':fields.boolean(string="Allow debit and credit"),
	}

	_defaults = {
	'allow_multi_sequence' : False,
	
		} 
	'''
	_defaults = {
	'allow_check_conf' : False,
	'show_sequence' : False,
		} 
	'''
class irsecuence(osv.Model):
	_inherit = 'ir.sequence'
	_columns = {
		'journal_id':fields.many2one('account.journal','sequence_ids')
		    }
