{
    'name': 'Servicio de Reparación',
    'version': '19.0.1.0.0',
    'category': 'Services/Repair',
    'summary': 'Gestión de reparaciones para flotas de camiones',
    'description': """
        Módulo para la gestión y seguimiento de órdenes de reparación
        de flotillas de camiones.
        Incluye manejo de clientes, flotas, órdenes de reparación detalladas
        y la capacidad de generar cotizaciones y facturas.
    """,
    'author': 'MBA Consulting',
    'website': 'https://www.mbaconsulting.com',
    'depends': [
        'base',
        'repair',
        'fleet',
        'sale_management',
        'hr',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_engine_hour_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/repair_order_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'wizard/repair_report_wizard_views.xml',
        'views/mecanico_views.xml',
        'views/menu_views.xml',
        'report/repair_report.xml',
        'report/repair_report_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
