# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt

from __future__ import unicode_literals

import os
import shutil
import unittest
import frappe
from recod_frappe_devtools.build_docs.setup_docs import SetupDocs


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.app_name = "recod_frappe_devtools"
        # Test doctype
        self.doctype_path = frappe.get_app_path('recod_frappe_devtools', 'recod_frappe_devtools', 'doctype')
        # if not os.path.isdir(os.path.join(self.doctype_path, 'mail_request')):
        #     os.mkdir(os.path.join(self.doctype_path, 'mail_request'))
        #     shutil.copyfile(
        #         frappe.get_app_path('recod_frappe_devtools', 'tests', 'test_doctype.json'),
        #         os.path.join(self.doctype_path, 'mail_request', 'mail_request.json'))
        self.setup_docs = SetupDocs(self.app_name, self.app_name, 'png')
        self.setup_docs.build('current')
        self.setup_docs.add_sidebars()

    def tearDown(self):
        if os.path.isdir(frappe.get_app_path('recod_frappe_devtools', 'www')):
            shutil.rmtree(frappe.get_app_path('recod_frappe_devtools', 'www'))

    def test_build_app_docs_sidebar_exists(self):
        sidebar_path = frappe.get_app_path("recod_frappe_devtools", 'www', 'docs', '_sidebar.json')
        self.assertTrue(os.path.isfile(sidebar_path))
        with open(frappe.get_app_path("recod_frappe_devtools", 'www', 'docs', '_sidebar.json'), 'r') as f:
            file_content = f.read()
        self.assertIn('''"route": "/docs/recod_frappe_devtools"''', file_content)
        self.assertIn('''"title": "Recod Frappe DevTools"''', file_content)

    def test_add_uml_file_exists(self):
        self.assertTrue(
            frappe.get_app_path("recod_frappe_devtools", 'www', 'docs', 'recod_frappe_devtools', 'assets',
                                'generated_uml.pdf'))

    def test_update_sidebars_in_all_apps_contain_app(self):
        self.setup_docs.update_sidebars_in_all_apps()
        self.assertIn('/docs/recod_frappe_devtools', str(self.setup_docs.list_sidebar))