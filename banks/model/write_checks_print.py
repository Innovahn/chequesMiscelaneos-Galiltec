from openerp.osv import osv
class reporte2(osv.AbstractModel):
	_name = 'report.banks.write_checks_print'
	def render_html(self, cr, uid, ids, data=None, context=None):
		report_obj = self.pool['report']
		report = report_obj._get_report_from_name(cr, uid, 'banks.write_checks_print')
		docargs = {
			'doc_ids': ids,
			'doc_model': report.model,
			'docs': self.pool[report.model].browse(cr, uid, ids, context=context),
			}
		return report_obj.render(cr, uid, ids, 'banks.write_checks_print',docargs, context=context)
