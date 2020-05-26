# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt

from __future__ import unicode_literals

import os
import unittest
import frappe
from recod_frappe_devtools.build_docs.setup_docs import SetupDocs
from recod_frappe_devtools.commands import _build_docs_once


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.app_name = "recod_frappe_devtools"
        setup_docs = SetupDocs(self.app_name, self.app_name, 'png')
        setup_docs.build('current')
        setup_docs.add_sidebars()

    def test_build_app_docs_one_checker(self):
        self.assertTrue(frappe.get_app_path("recod_frappe_devtools", 'www'))

    def test_add_uml_file_exists(self):
        self.assertTrue(frappe.get_app_path("recod_frappe_devtools", 'www', 'docs', 'recod_frappe_devtools', 'assets',
                                            'generated_uml.pdf'))
