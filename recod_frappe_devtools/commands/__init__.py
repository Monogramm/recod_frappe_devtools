from __future__ import unicode_literals, absolute_import
import click
import frappe
from frappe.commands import pass_context


@click.command('build-app-docs')
@pass_context
@click.argument('app')
@click.option('--docs-version', default='current')
def build_app_docs(context, app, docs_version="current"):
    for site in context.sites:
        _build_docs_once(site, app, docs_version)


def _build_docs_once(site, app, docs_version, only_content_updated=False):
    from frappe.utils.setup_docs import setup_docs

    try:
        frappe.init(site=site)
        frappe.connect()
        make = setup_docs(app, app)  # Not so good. The similar parameters

        if not only_content_updated:
            make.build(docs_version)

    finally:
        frappe.destroy()


commands = [
    build_app_docs,
]
