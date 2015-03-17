# -*- coding: utf-8 -*-
{	
	'name' : 'Banks and Saving Bank',
	'author': 'Grupo Innova',
	'category': 'Banks/Accounting',
	'summary': ' ',
	'description': """   """,

	'data':[
		#'views/create_bank.xml',
		#'views/create_checkbook.xml',
		'views/journal_view.xml',
		'views/account_voucher.xml',
		'views/write_checks.xml',
		],	
	'update_xml' : [
			'security/groups.xml',
			#'security/ir.model.access.csv',
	],
	'depends': ['base','account'],
    	'installable': True,
}
