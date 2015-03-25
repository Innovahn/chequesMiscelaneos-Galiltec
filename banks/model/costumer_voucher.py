# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
import locale
import pytz
from openerp.tools.translate import _
import time
from itertools import ifilter
class account_voucher(osv.Model):
	bandera=0
	#this function retuns the id of the sequence for the transation type(check,transaction) for the costumer invoice
	def _get_sequence(self, cr, uid,  ids, journalid, context=None):
		for invoice in self.browse(cr,uid,ids,context=context):
			doc_type = invoice.pay_method_type
			journalid=invoice.journal_id.id
		if doc_type is False:
			doc_type = 'deposit'
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
		if doc_type is None:#si no biene nada en el doc_type se asume que es un deposito, luego se evaluara contexto y cambiara en base a las siguientes lineas, 
			doc_type= 'deposit'
		if context is None:
			context={}
			if journalid and doc_type:		
				journalid = journalid
				doc_type = doc_type
			else:
				for invoice in self.browse(cr,uid,ids,context=None):
					doc_type = invoice.pay_method_type
					journalid=invoice.journal_id.id
		else:
			#if context.get('write_check'):#si el contexto tiene writecheck no se deberia mostrar frecuancia de deposito,
			#	doc_type = 'check'
			
			if journalid and doc_type:		
				journalid = journalid
				doc_type = doc_type
			else:
				for invoice in self.browse(cr,uid,ids,context=None):
					doc_type = invoice.pay_method_type
					journalid=invoice.journal_id.id

			if context.get('journal_type'):
				if context['journal_type']=='sale':
					doc_type ='deposit'
					for invoice in self.browse(cr,uid,ids,context=None):
						journalid=invoice.journal_id.id
		if not journalid==False and doc_type != False:
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

	def get_doc_type(self, cr, uid, ids, context=None):
		for invoice in self.browse(cr,uid,ids,context=context):
			return invoice.pay_method_type
			
	#override function that is raised when the button is push
	def button_proforma_voucher(self, cr, uid, ids, context=None):
		
		self.write(cr,uid,ids,{'sequence_id':self.next_seq_number(cr,uid,ids,None,None,'seq_id'),'number_doc':self.get_number_name(cr, uid, ids, context=context)},context=context)
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
	def _sale_o_purch(self, cr, uid, ids, field, arg, context=None):
		result={}
		for invoice in self.browse(cr,uid,ids,context=context):
			result[invoice.id]=invoice.pay_method_type
		return result 

	def get_number_onchange_journal(self, cr, uid, ids, doc_type, context=None):#encapsulate function to get
		if context.get('write_check'):
			n=self.next_seq_number(cr,uid,ids,journal.id,self.get_doc_type(cr,uid,ids,context=context),'pcabrera',context=context)#Line agregated
		else:
       			n=self.next_seq_number(cr,uid,ids,journal.id,self.get_doc_type(cr,uid,ids,context=context),'pcabrera',context=context)#Line agregated
		return 
 		

	#override function of onchange journal and i agregated the update of the values of number(next prefix for sequence) in this function
	def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, doc_type, context=None):
	        if context is None:
		        context = {}
       		if not journal_id:
            		return False
        	journal_pool = self.pool.get('account.journal')
      		journal = journal_pool.browse(cr, uid, journal_id, context=context)
       		account_id = journal.default_credit_account_id or journal.default_debit_account_id
       		tax_id = False
       		if account_id and account_id.tax_ids:
        		tax_id = account_id.tax_ids[0].id

    	   	vals = {'value':{} }
     		if ttype in ('sale', 'purchase'):
         		vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
          		vals['value'].update({'tax_id':tax_id,'amount': amount})
       		currency_id = False
       		if journal.currency:
         		currency_id = journal.currency.id
       		else:
          		currency_id = journal.company_id.currency_id.id
		period_ids = self.pool['account.period'].find(cr, uid, context=dict(context, company_id=company_id))
		if context.get('write_checks'):
			n=self.next_seq_number(cr,uid,ids,journal.id,doc_type,'pcabrera',context=context)#Line agregated
		else:
			n=self.next_seq_number(cr,uid,ids,journal.id,self.get_doc_type(cr,uid,ids,context=context),'pcabrera',context=context)#Line agregated
		
        	vals['value'].update({
			'number_doc' : n,
			'next_number' : n,
           		'currency_id': currency_id,
           		'payment_rate_currency_id': currency_id,
           		'period_id': period_ids and period_ids[0] or False
      		})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
     		if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
      			vals['value']['amount'] = 0
        		amount = 0
       		if partner_id:
           		res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
          		for key in res.keys():
            			vals[key].update(res[key])
       		return vals

	
	def _get_totalt(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for check in self.browse(cr,uid,ids,context=context):
			a=self.to_word(check.amount, check.currency_id.name)
			result[check.id]=a
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
		'amounttext': fields.function(_get_totalt,type='char',string='Total',),
	}

	_defaults={
	'pay_method_type': 'check'		
	}

	def to_word(self,number, mi_moneda):
	    valor= number
	    number=int(number)
	    centavos=int((round(valor-number,2))*100)
	    UNIDADES = (
	    '',
	    'UN ',
	    'DOS ',
	    'TRES ',
	    'CUATRO ',
	    'CINCO ',
	    'SEIS ',
	    'SIETE ',
	    'OCHO ',
	    'NUEVE ',
	    'DIEZ ',
	    'ONCE ',
	    'DOCE ',
	    'TRECE ',
	    'CATORCE ',
	    'QUINCE ',
	    'DIECISEIS ',
	    'DIECISIETE ',
	    'DIECIOCHO ',
	    'DIECINUEVE ',
	    'VEINTE '
	)

	    DECENAS = (
	    'VENTI',
	    'TREINTA ',
	    'CUARENTA ',
	    'CINCUENTA ',
	    'SESENTA ',
	    'SETENTA ',
	    'OCHENTA ',
	    'NOVENTA ',
	    'CIEN '
	)

	    CENTENAS = (
	    'CIENTO ',
	    'DOSCIENTOS ',
	    'TRESCIENTOS ',
	    'CUATROCIENTOS ',
	    'QUINIENTOS ',
	    'SEISCIENTOS ',
	    'SETECIENTOS ',
	    'OCHOCIENTOS ',
	    'NOVECIENTOS '
	)
	    MONEDAS = (
		    {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		    {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
		    {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
		    {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		    {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		    {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
		    {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
		)
	    if mi_moneda != None:
		try:
		    moneda = ifilter(lambda x: x['currency'] == mi_moneda, MONEDAS).next()
		    if number < 2:
		        moneda = moneda['singular']
		    else:
		        moneda = moneda['plural']
		except:
		    return "Tipo de moneda inválida"
	    else:
		moneda = ""
	    """Converts a number into string representation"""
	    converted = ''

	    if not (0 < number < 999999999):
		return 'No es posible convertir el numero a letras'

	    number_str = str(number).zfill(9)
	    millones = number_str[:3]
	    miles = number_str[3:6]
	    cientos = number_str[6:]

	    if(millones):
		if(millones == '001'):
		    converted += 'UN MILLON '
		elif(int(millones) > 0):
		    converted += '%sMILLONES ' % self.convert_group(millones)

	    if(miles):
		if(miles == '001'):
		    converted += 'MIL '
		elif(int(miles) > 0):
		    converted += '%sMIL ' % self.convert_group(miles)

	    if(cientos):
		if(cientos == '001'):
		    converted += 'UN '
		elif(int(cientos) > 0):
		    converted += '%s ' % self.convert_group(cientos)
	    if(centavos)>0:
		converted+= "con %2i/100 "%centavos
	    converted += moneda

	    return converted.title()


	def convert_group(self,n):
	    UNIDADES = (
	    '',
	    'UN ',
	    'DOS ',
	    'TRES ',
	    'CUATRO ',
	    'CINCO ',
	    'SEIS ',
	    'SIETE ',
	    'OCHO ',
	    'NUEVE ',
	    'DIEZ ',
	    'ONCE ',
	    'DOCE ',
	    'TRECE ',
	    'CATORCE ',
	    'QUINCE ',
	    'DIECISEIS ',
	    'DIECISIETE ',
	    'DIECIOCHO ',
	    'DIECINUEVE ',
	    'VEINTE '
	)

	    DECENAS = (
	    'VENTI',
	    'TREINTA ',
	    'CUARENTA ',
	    'CINCUENTA ',
	    'SESENTA ',
	    'SETENTA ',
	    'OCHENTA ',
	    'NOVENTA ',
	    'CIEN '
	)

	    CENTENAS = (
	    'CIENTO ',
	    'DOSCIENTOS ',
	    'TRESCIENTOS ',
	    'CUATROCIENTOS ',
	    'QUINIENTOS ',
	    'SEISCIENTOS ',
	    'SETECIENTOS ',
	    'OCHOCIENTOS ',
	    'NOVECIENTOS '
	)
	    MONEDAS = (
		    {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		    {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
		    {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
		    {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		    {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		    {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
		    {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
		)
	    """Turn each group of numbers into letters"""
	    output = ''

	    if(n == '100'):
		output = "CIEN "
	    elif(n[0] != '0'):
		output = CENTENAS[int(n[0]) - 1]

	    k = int(n[1:])
	    if(k <= 20):
		output += UNIDADES[k]
	    else:
		if((k > 30) & (n[2] != '0')):
		    output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
		else:
		    output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])

	    return output

	def addComa(self, snum ):
		s = snum;
		i = s.index('.') # Se busca la posición del punto decimal
		while i > 3:
			i = i - 3
			s = s[:i] +  ',' + s[i:]
		return s

