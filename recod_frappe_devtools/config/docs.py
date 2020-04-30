# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt
"""Configuration for docs."""

from __future__ import unicode_literals


source_link = "https://github.com/Monogramm/recod_frappe_devtools"
docs_base_url = "https://monogramm.github.io/recod_frappe_devtools"
headline = "Frappe application to provide more/better development tools."
sub_heading = "Build app documentation and development helpers."


def get_context(context):
    """Returns the application documentation context.

     :param context: application documentation context"""
    context.brand_html = "Recod Frappe DevTools"
    context.source_link = source_link
    context.docs_base_url = docs_base_url
    context.headline = headline
    context.sub_heading = sub_heading
