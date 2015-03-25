# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime

class irsecuence(osv.Model):
	_inherit = 'ir.sequence'
	_columns = {
		'journal_id':fields.many2one('account.journal','sequence_ids')
		    }
