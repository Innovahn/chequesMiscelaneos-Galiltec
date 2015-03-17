# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
import locale
import pytz
from openerp.tools.translate import _
import time
from itertools import ifilter
class account_invoice(osv.Model):
	#this function retuns the id of the sequence for the transation type(check,transaction) for the costumer invoice
	def _get_sequence(self, cr, uid,  ids, journalid, context=None):
		
		for invoice in self.browse(cr,uid,ids,context=context):
			doc_type = invoice.pay_method_type
			journalid=invoice.journal_id.id
		journal_obj = self.pool.get('account.journal')
		diario = journal_obj.browse(cr,uid,journal_obj.search(cr,uid,[('id','=',journalid)],context=None),context=context)
		seq_id=0
		for sq in diario.sequence_ids:
			if sq.code == doc_type:
				seq_id = sq.id
				return seq_id
		return False
	#this funtion return the next number of the check or transaction
	def next_seq_number(self,cr,uid,ids,journalid,doc_type,seq_o_name,context=None):
		if journalid and doc_type:		
			journalid = journalid
			doc_type = doc_type
		else:
			for invoice in self.browse(cr,uid,ids,context=context):
				doc_type = invoice.pay_method_type
				journalid=invoice.journal_id.id
	
		if context is None:
			context={}	
		if not journalid==False and doc_type !=False:
			journal_obj = self.pool.get('account.journal')
			diario = journal_obj.browse(cr,uid,journal_obj.search(cr,uid,[('id','=',journalid)],context=None),context=context)
			seq_id=0
			fl=False
			for sq in diario.sequence_ids:
				if sq.code == doc_type:
					seq_id = sq.id
					if seq_o_name=='seq_id':
						return seq_id
					fl = True
			if not fl:
				raise osv.except_osv(_('Configuration Error !'),_("Please Create a sequence code with the code '"+str(doc_type)+"' and add this sequence to the journal ''!"))	
		
			if diario.sequence_id:
				if not diario.sequence_id.active:
					raise osv.except_osv(_('Configuration Error !'),_('Please activate the sequence of selected journal !'))
				#c = dict(context)
				seq_model = self.pool.get('ir.sequence')
				obj_seq = seq_model.browse(cr, uid, seq_model.search(cr,uid,[('id','=',int(seq_id))],context=None))
				if obj_seq['implementation'] == 'standard':
					cr.execute("SELECT nextval('ir_sequence_%03d')" % obj_seq['id'])
					r=cr.fetchone()
					obj_seq['number_next'] = cr.fetchone()
     				else:
       					cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (obj_seq['id'],))
          		       		seq_model.invalidate_cache(cr, uid, ['number_next'], [obj_seq['id']], context=context)
				d = obj_seq._interpolation_dict()
				try:
          				interpolated_prefix = obj_seq._interpolate(obj_seq['prefix'], d)
           				interpolated_suffix = obj_seq._interpolate(obj_seq['suffix'], d)
       				except ValueError:
       					raise osv.except_osv(_('Warning'), _('Invalid prefix or suffix for sequence \'%s\'') % (obj_seq.get('name')))
     				name = interpolated_prefix + '%%0%sd' % obj_seq['padding'] % obj_seq['number_next'] + interpolated_suffix
				return  name
			else:
				return False

	#override function that is used for account.voucher to create the account move, and account move line(location/adoo/addons/account_voucher/account_voucher.py linea 1043)
	def account_move_get(self, cr, uid, voucher_id, context=None):
		seq_obj = self.pool.get('ir.sequence')
	        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
		if voucher.number:
	        	name = voucher.number
	        elif voucher.journal_id.sequence_id:
	        	if not voucher.journal_id.sequence_id.active:
	        	        raise osv.except_osv(_('Configuration Error !'),
	        	            _('Please activate the sequence of selected journal !'))
	        	c = dict(context)
	           	c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
			seq_id=self._get_sequence(cr, uid, voucher_id,voucher.journal_id.id, context=None)
			if seq_id:
				name = seq_obj.next_by_id(cr, uid, seq_id, context=c)		
			else:
	           		name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
	        else: 
	        	raise osv.except_osv(_('Error!'),_('Please define a sequence on the journal.'))
	        if not voucher.reference:
	        	ref = name.replace('/','')
	        else:
	        	ref = voucher.reference
	
	        move = {
	        	'name': name,
	        	'journal_id': voucher.journal_id.id,
	                'narration': voucher.narration,
	                'date': voucher.date,
	                'ref': ref,
	                'period_id': voucher.period_id.id,
	        }
	        return move

	def get_number_name(self, cr, uid, ids, context=None):
		for invoice in self.browse(cr,uid,ids,context=context):
			return invoice.number_doc

	#override function that is raised when the button is push
	def button_proforma_voucher(self, cr, uid, ids, context=None):
		
		self.write(cr,uid,ids,{'sequence_id':self.next_seq_number(cr,uid,ids,None,None,'seq_id'),'number_doc':self.get_number_name(cr, uid, ids, context=None)},context=context)
		self.signal_workflow(cr, uid, ids, 'proforma_voucher')
       		return {'type': 'ir.actions.act_window_close'}
	
	def onchange_journal_id(self,cr,uid,ids,journalid,doctype,context=None):
		n=self.next_seq_number(cr,uid,ids,journalid,doctype,'pcabrera',context=context)
		return { 'value' :{ 'number_doc' : n,'next_number' : n}}#send both because number field is never entry


	def _next_number(self, cr, uid, ids, field, arg, context=None):
		result={}
		for invoice in self.browse(cr,uid,ids,context=context):
			result[invoice.id]=invoice.number_doc
		return result 


	def _doc_type(self, cr, uid, ids, field, arg, context=None):
		result={}
		for invoice in self.browse(cr,uid,ids,context=context):
			result[invoice.id]=invoice.pay_method_type
		return result 
	

	_inherit = 'account.voucher'
	_columns = {
		'pay_method_type':fields.selection([
						('check','Check'),
						('transference','Transference')],string='Pay type'),
		'sequence_id':fields.many2one('ir.sequence','Sequence id'),
		'number_doc' : fields.char(string = 'Number'),
		'next_number' : fields.function(_next_number,type='char',string='Next number',help='The number of the next check or transaction',store=False),
		'doc_type' : fields.function(_doc_type,type='char',string='Doc type',help='Choose the paying method',store=False),
	}


