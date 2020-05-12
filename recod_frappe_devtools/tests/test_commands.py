# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt

from __future__ import unicode_literals

import os
import unittest
import frappe
from recod_frappe_devtools.commands import _build_docs_once


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.context = {'sites': frappe.utils.get_sites(), 'force': False, 'verbose': False, 'profile': False}
        _build_docs_once(self.context['sites'][0], "recod_frappe_devtools", "current", "recod_frappe_devtools", "local")

    def test_build_app_docs_one_checker(self):
        self.assertTrue(frappe.get_app_path("recod_frappe_devtools", 'www'))

    def test_add_uml_file_exists(self):
        self.assertTrue(frappe.get_app_path("recod_frappe_devtools", 'www', 'docs', 'recod_frappe_devtools', 'assets',
                                            'generated_uml.pdf'))
