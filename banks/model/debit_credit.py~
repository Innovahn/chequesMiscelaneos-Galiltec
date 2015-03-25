# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
import locale
import pytz
from openerp.tools.translate import _
import time
from itertools import ifilter
class mcheck(osv.Model):
	_order = 'date desc'
	_name = 'debit.credit'


	def cancel_voucher(self, cr, uid, ids, context=None):
		reconcile_pool = self.pool.get('account.move.reconcile')
		chck_memo = ''
		for mcheck in self.browse(cr,uid,ids,context=context):
			check_move = self.pool.get('account.move')
			check_move_obj=check_move.browse(cr,uid,check_move.search(cr,uid,[('id','=',mcheck.move_id.id )],context=None),context=context)
			move_line = self.pool.get('account.move.line')
			move_l_obj=move_line.browse(cr,uid,move_line.search(cr,uid,[('move_id','=',check_move_obj.id )],context=None),context=context)
			move_values = {}
			account_period = self.pool.get('account.period')
			selected_cancel_date=datetime.now()
			if mcheck.anulation_date:
				selected_cancel_date=mcheck.anulation_date#selected date for tha cancelation 
			
			account_period_obj = account_period.browse(cr,uid,account_period.search(cr,uid,['&','&',( 'date_start','<=', selected_cancel_date),('date_stop', '>=',selected_cancel_date),('special','<>',True)],context=None),context=context)
			for obj in check_move_obj:
				move_values['date'] = datetime.now()
				move_values['journal_id'] = obj['journal_id'].id
				move_values['name']=str(obj['name'])+str('/Cancel')
				move_values['period_id']=account_period_obj.id
				move_values['ref']=obj['ref']
				move_values['narration'] = 'Annulment of check '+mcheck.number + ' from ' + mcheck.date
				
			move_id = check_move.create(cr,uid,move_values)
			move_l_values = {}
			move_l_values['date'] = datetime.now()
			for lines2 in move_l_obj:
				move_l_values['name'] = lines2['name']
				move_l_values['account_id'] = lines2['account_id'].id
				move_l_values['credit_debit_id'] = lines2['credit_debit_id'].id
				move_l_values['analytic_account_id']= lines2['analytic_account_id'].id
				move_l_values['move_id'] = move_id		
				move_l_values['currency_id'] = lines2['currency_id'].id
				move_l_values['amount_currency'] = lines2['amount_currency']
			
				if lines2.credit == 0:
					move_l_values['debit'] = 0
					move_l_values['credit'] = lines2.debit
					move_l_values['amount_currency'] = lines2['amount_currency']*(-1)
			
				else:
					move_l_values['credit'] = 0
					move_l_values['debit'] = lines2.credit
					move_l_values['amount_currency'] = lines2['amount_currency']*(-1)
				
				move_line.create(cr,uid,move_l_values)
			for lin in mcheck.mcheck_ids:
				if lin.name:
					new_name = 'Annulment of check '+mcheck.number+ ' ' + str(lin.name)
				else:
					new_name = 'Annulment of check '+mcheck.number
				self.write(cr, uid, ids,{'mcheck_ids': [(1,lin.id,{'name':new_name})]}, context=context)
			if mcheck.name:
				chck_memo = mcheck.name
			else:
				chck_memo = 'Annulment of check '+mcheck.number
		return self.write(cr, uid, ids, {'state':'anulated','name':chck_memo}, context=context)
				
	

			
	

	def action_validate(self, cr, uid, ids, context=None):
		corrency_rate = 0.0
		model_currency_rate = None
		decimal_precision = self.pool.get('decimal.precision')
		dec_prec = decimal_precision.browse(cr,uid,decimal_precision.search(cr,uid,[('name' , '=', 'Account' )],context=None),context=context)
		for m in self.browse(cr,uid,ids,context=context):
			model_user = self.pool.get('res.users')
			obj_user = model_user.browse(cr,uid,model_user.search(cr,uid,[('id' , '=', uid )],context=None),context=context)
			model_company = self.pool.get('res.company')
			
			obj_company = model_company.browse(cr,uid,model_company.search(cr,uid,[('id' , '=', obj_user.company_id.id )],context=None),context=context)
			
			
		cr.execute('SELECT rc.id,rc.name AS currency_name,rcr.write_date,rcr.create_date,rcr.rate,rcr.name,rcr.currency_id  FROM res_currency_rate AS rcr,res_currency AS rc WHERE rcr.currency_id = rc.id AND rc.active= True AND rcr.currency_id=%s AND rcr.name <= now() ORDER BY rcr.write_date DESC  LIMIT 1',(obj_company.currency_id.id,))
		i=0
		
		for obg_rate in cr.fetchall():
			currency_rate = obg_rate[4]#currency for tha company thah im linked with
		currency_id = obj_company.currency_id.id #id of the currency for tha company thah im linked with
		#id of the currency for tha company thah im linked with
		select_journal_currency_name  = obj_company.currency_id.name#name of the secundary currency  of a journal if it have it
			

		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				flag=True
				
				select_journal_currency_id =mcheck.journal_id.currency.id#the currency of the journal selected, if it dosent have it, it will see if the default account have a currency, in defect it will be the default company currency
				if select_journal_currency_id:
				
					cr.execute('SELECT rc.id,rc.name AS currency_name,rcr.write_date,rcr.create_date,rcr.rate,rcr.name,rcr.currency_id  FROM res_currency_rate AS rcr,res_currency AS rc WHERE rcr.currency_id = rc.id  AND rc.active= True AND rcr.currency_id=%s AND rcr.name <= now() ORDER BY rcr.write_date DESC  LIMIT 1',(select_journal_currency_id,))
					i=0
					obg_rate1=cr.fetchall()
					if len(obg_rate1)>0:
						for r in obg_rate1:
							select_journal_currency_rate = r[4] #rate of the currently selected journal				
							select_journal_currency_name = r[0]
							
					else:
						raise osv.except_osv(_('Error!'),_("The selected journal must have a currency rate asociadted") )
								
				else: 
					
						select_journal_currency_rate = currency_rate 
						select_journal_currency_id = currency_id
				account_period = self.pool.get('account.period')
				account_period_obj = account_period.browse(cr,uid,account_period.search(cr,uid,['&','&',( 'date_start','<=', mcheck.date ),('date_stop', '>=',mcheck.date),('special','<>',True)],context=None),context=context)
				for line in mcheck.mcheck_ids:
					total+=line.amount
					if line.amount <= 0:
						flag=False
					if line.type=='dr':
						totald+=line.amount
					if line.type=='cr':
						totalc+=line.amount
				
				totalc_curr = 0
				totald_curr = 0
				totald=0
				totalc=0
				lines_array=[]
				name = "/"
				if mcheck.number:
					name=mcheck.number
				amove_obj= self.pool.get('account.move')
				amovedata={}
				amovedata['journal_id']=mcheck.journal_id.id
				amovedata['name']=name
				amovedata['date']=mcheck.date
				amovedata['period_id']=account_period_obj.id
				amovedata['ref']=mcheck.name					
				seq_obj = self.pool.get('ir.sequence')

				move_id= amove_obj.create(cr,uid,amovedata)
				mline_obj= self.pool.get('account.move.line')
				for lines in mcheck.mcheck_ids:
					lines_col={}
					lines_col['move_id']=move_id
					lines_col['account_id']=lines.account_id.id
					lines_col['name']=lines.name  or '/'
					if lines.type == 'dr':
							lines_col['credit']=0
							
							if (select_journal_currency_rate !=0):
								lines_col['debit'] = round((lines.amount * (1/select_journal_currency_rate))*currency_rate,dec_prec.digits)
							else:
								lines_col['debit'] = round(lines.amount * currency_rate,dec_prec.digits)
							totald+=lines_col['debit']
							if select_journal_currency_id == currency_id:#si el currency de 
								#lines_col['amount_currency'] = None
								#lines_col['currency_id'] = None
								totald_curr+=lines_col['debit']
							else:
								lines_col['amount_currency']=(lines.amount * (1/select_journal_currency_rate))*select_journal_currency_rate#shame on me, hahahaha 1(x/y)y=x
								lines_col['currency_id'] = select_journal_currency_id
								totald_curr+=lines.amount
							
														
					else:
							lines_col['debit']=0
							lines_col['credit'] = round(((lines.amount * (1/select_journal_currency_rate))*currency_rate),dec_prec.digits)
							totalc+=lines_col['credit']  #total of debit multiplicated by default
							if select_journal_currency_id == currency_id:
								#lines_col['currency_id'] = None
								#lines_col['amount_currency']=None
								totalc_curr+=lines_col['credit']
							else:
								lines_col['amount_currency'] = (lines.amount * (1/select_journal_currency_rate))*(-1)*select_journal_currency_rate
								lines_col['currency_id'] = select_journal_currency_id
								totalc_curr+=lines.amount
					lines_col['move_id']=move_id
					lines_col['date']=mcheck.date
					lines_col['credit_debit_id']=mcheck.id
					lines_col['analytic_account_id']=lines.chqmanalitics.id
					lines_array.append(lines_col)
				mline_data={}
				mline_data['move_id']=move_id
				mline_data['name'] = mcheck.name
				mline_data['credit']= totald-totalc
				mline_data['debit']=0
				mline_data['date']=mcheck.date
				if not (currency_id == select_journal_currency_id):
					mline_data['currency_id'] = select_journal_currency_id
					mline_data['amount_currency']=((totald_curr-totalc_curr) * (1/select_journal_currency_rate)*select_journal_currency_rate)*(-1)
						
					
				mline_data['account_id']=mcheck.journal_id.default_credit_account_id.id
				mline_data['credit_debit_id']=mcheck.id
				if round(totald_curr-totalc_curr,dec_prec.digits ) != round(mcheck.total,dec_prec.digits ):
					raise osv.except_osv(_('you still have '+str(mcheck.total-(totald_curr-totalc_curr))),_("Try to make it fit") )
				
					
				line_id= mline_obj.create(cr,uid,mline_data)
				for lines2 in lines_array:
					mline_obj.create(cr,uid,lines2)
					
				if currency_id == select_journal_currency_id:
					select_journal_currency_rate = False
				for lin in mcheck.mcheck_ids:
					if not lin.name:
						new_name = mcheck.name
						self.write(cr, uid, ids,{'mcheck_ids': [(1,lin.id,{'name':new_name})]}, context=context)
				n=self.journal_number(cr,uid,mcheck.id,mcheck.journal_id.id,mcheck.doc_type,context=None)
				try:
					journa_obj = self.pool.get('account.journal')
					diario = journa_obj.browse(cr,uid,journa_obj.search(cr,uid,[('id','=',mcheck.journal_id.id)],context=None),context=context)
					seq_id=0
					fl=False
					for sq in diario.sequence_ids:
						if sq.code==mcheck.doc_type:
							seq_id=sq.id
							fl=True
					if fl:
						cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq_id,))
					else:						
						raise osv.except_osv(_('Error !'),_("Could't update the sequence for this journal!"))
						
				except ValueError:
					raise osv.except_osv(_('Update Error!'),_("Sequence value was not updated") )

				mchecks_model = self.pool.get('debit.credit')
				mchecks_obj=mchecks_model.browse(cr,uid,mchecks_model.search(cr,uid,[('state','=','draft' )],context=None),context=context)
				nn=self.journal_number(cr,uid,mcheck.id,mcheck.journal_id.id,mcheck.doc_type,context=None)
				for draft_checks in mchecks_obj:
					mchecks_model.write(cr, uid, draft_checks.id, {'number':nn}, context=context)

				return self.write(cr, uid, ids, {'state':'validated','number':n,'move_id':move_id, 'actual_comp_rate': currency_rate,'actual_sec_curr_rate': select_journal_currency_rate }, context=context)
		else:
			raise osv.except_osv(_('No lines'),_("select more than one line") )
		
	def _get_totald(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				for lines in mcheck.mcheck_ids:
					total+=lines.amount
					if lines.type=='dr':
						totald+=lines.amount
					if lines.type=='cr':
						totalc+=lines.amount
			result[mcheck.id]=self.addComa('%.2f'%(totald-totalc))
		return result	
	def _get_totaldebit(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.move_ids) > 0:
				totald=0
				for lines in mcheck.move_ids:
					totald+=lines.debit
			result[mcheck.id]=self.addComa('%.2f'%(totald))
		return result	
	def _get_totalcredit(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.move_ids) > 0:
				totalc=0
				for lines in mcheck.move_ids:
					totalc+=lines.credit
			result[mcheck.id]=self.addComa('%.2f'%(totalc))
		return result	


	def _get_totalt(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				for lines in mcheck.mcheck_ids:
					total+=lines.amount
					if lines.type=='dr':
						totald+=lines.amount
					if lines.type=='cr':
						totalc+=lines.amount
			if(mcheck.journal_id.currency):
				a=self.to_word(totald-totalc,mcheck.journal_id.currency.name)
			else:
				a=self.to_word(totald-totalc,'HNL')
			result[mcheck.id]=a
		return result

	def _paying_left(self,cr, uid, ids, field, arg, context=None):
		result = {}
		tot_lined = 0
		tot_linec = 0
		for mcheck in self.browse(cr,uid,ids,context=context):
			for lines in mcheck.mcheck_ids:
				if lines.type=='dr':
					tot_lined+=lines.amount
				else:
					tot_linec+=lines.amount
					
			result[mcheck.id]=mcheck.total-(tot_lined-tot_linec)
		return result
	def anulate_voucher(self,cr, uid, ids, context=None):
		self.write(cr, uid, ids,{'state':'pre_anulated'}, context=context)

	def journal_number(self,cr,uid,ids,journalid,doc_type,context=None):
		#print '{{'*100
		#print doc_type
		if not journalid==False and doc_type !=False:
			force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id#id of the company of the user
			seq_model = self.pool.get('ir.sequence')
			name = "/"
			journal_obj = self.pool.get('account.journal')
			diario = journal_obj.browse(cr,uid,journal_obj.search(cr,uid,[('id','=',journalid)],context=None),context=context)
			seq_id=0
			fl=False
			for sq in diario.sequence_ids:
				if sq.code == doc_type:
					seq_id = sq.id
					fl = True
			if not fl:
				raise osv.except_osv(_('Configuration Error !'),_("Please Create a sequence code with the code '"+str(doc_type)+"' or add a sequence for this journal with the code '"+str(doc_type)+"'"))	
		
			if diario.sequence_id:
				if not diario.sequence_id.active:
					raise osv.except_osv(_('Configuration Error !'),_('Please activate the sequence of selected journal !'))
				#c = dict(context)
				obj_seq = seq_model.browse(cr, uid, seq_model.search(cr,uid,[('id','=',int(seq_id))],context=None))
				if obj_seq['implementation'] == 'standard':
					cr.execute("SELECT nextval('ir_sequence_%03d')" % obj_seq['id'])
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
	def onchange_journal(self,cr,uid,ids,journalid,doc_type,context=None):
		n=self.journal_number(cr,uid,ids,journalid,doc_type,context=None)
		return { 'value' :{ 'number' : n,'number_calc' : n}}
		
	

	def create(self, cr, uid, values, context=None):
		b =super(mcheck, self).create(cr, uid, values, context=context)
		if b:
			
			return b
		else:	
			return False		
	#def _currence_factor(self, cr, uid, ids, context=None):
	def _calculate_number(self,cr, uid, ids, field, arg, context=None):
		result={}
		for mcheck in self.browse(cr,uid,ids,context=context):
			result[mcheck.id]=mcheck.number
		return result
				
			
		
	_columns={
        'move_id':fields.many2one('account.move', 'Account Entry', copy=False),
	                'journal_id':fields.many2one('account.journal', 'Journal',required=True ),
		'name':fields.text('Memo', required=True),
		'date':fields.date('Date',  select=True, 
                           help="Effective date for accounting entries", ),
		'amount': fields.function(_get_totald,type='char',string='Total', ),
		'amountdebit': fields.function(_get_totaldebit,type='char',string='Total', ),
		'amountcredit': fields.function(_get_totalcredit,type='char',string='Total',),
		'amounttext': fields.function(_get_totalt,type='char',string='Total',),
		'total': fields.float(string='Total',required=True),
		#'temporal_code': fields.char(string='Temporal Code',),
		'doc_type' : fields.selection([
						('debit','Debit'),
						('credit','Credit')],string='Type'),
		'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), ),
		#'reference': fields.char('Pay to', 
		#                         help="Transaction reference number.", copy=False,required=True),
		'rest_credit' : fields.function(_paying_left, type='float', string='Debit left', store=False),
		'actual_comp_rate' : fields.float('Company rate'),
		'actual_sec_curr_rate' : fields.float('Actual Secundary Currency Rate'), #date of the anulation of the check
		#'currency_rate' : fields.function(_calculate_currency,type='float')
		'number': fields.char('Number'),
		'number_calc': fields.function(_calculate_number, type='char', string='Number', store=False),
		'obs':fields.text('obs',  ),
        	'type':fields.selection([
			('sale','Sale'),
			('purchase','Purchase'),
			('payment','Payment'),
			('receipt','Receipt'),
			],'Default Type', ),		 
		'mcheck_ids' :fields.one2many('debit.credit.name','mcheck_id',string="Debit and Credit lines"),
		'move_ids' :fields.one2many('account.move.line','credit_debit_id',string="Move lines"),
		'state':fields.selection(
		    [('draft','Draft'),
		     ('validated','Validated')
		    ], 'Status', 
		    help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
		                \n* The \'Validated \' when validated'),

	}
	_defaults = {
	'state' : 'draft',
	'type' : 'payment',
 	'date': lambda *a: time.strftime('%Y-%m-%d'),
	'doc_type' : 'debit'
		    } 
	
	
	
	# Para definir la moneda me estoy basando en los código que establece el ISO 4217
	# Decidí poner las variables en inglés, porque es más sencillo de ubicarlas sin importar el país
	# Si, ya sé que Europa no es un país, pero no se me ocurrió un nombre mejor para la clave.


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




class mcheck_name(osv.Model):
			
	_name='debit.credit.name'
		
	
	def onchange_amount_line(self,cr,uid,ids,total,ids_line,context=None):	

		
		total_line=0.0
		
		
	
	_columns = {
		'mcheck_id':fields.many2one('debit.credit','debit and credit '),
	        'account_id':fields.many2one('account.account','Account',domain=[('type','not in',['view'])],required=True),
		'name':fields.char('Description',),
		'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),
		'chqmanalitics':fields.many2one("account.analytic.account",string="Check Misc Analiticos"),	
        	'type':fields.selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr'),
		
}

	_defaults = {
	'type' : 'dr',
		} 
class account_move_line(osv.osv):
	_inherit = 'account.move.line'
	_columns = {
		'credit_debit_id':fields.many2one('debit.credit','debit.credit'),
		}
