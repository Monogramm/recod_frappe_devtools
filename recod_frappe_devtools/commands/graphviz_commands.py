# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt
"""Generate UML diagrams for a project

Call from command line:

	bench build-app-uml app path

"""
from __future__ import unicode_literals, absolute_import

import json
import os

import frappe
from graphviz import Digraph


def create_dot(json_dump, dot):
    """Create node for selected doctype"""
    label = json_dump['name'] + "|"
    links = []
    for field in json_dump['fields']:
        options = field.get('options') if field.get('options') else ""
        if field['fieldtype'] == 'Select':
            options = options.replace('\n', ", ")
        if field['fieldtype'] not in ("HTML"):
            label += "+ {}: {} {}\l".format(field['fieldname'], field['fieldtype'],
                                            "(" + options + ")" if options else "")
        if field['fieldtype'] in ('Link', "Table"):
            links.append({'head': json_dump['name'], 'end': field['options']})
    label = "{" + label + "}"
    dot.node(json_dump['name'], label, shape="record")
    for link in links:
        dot.edge(link['head'], link['end'])
    return dot


def get_all_modules(app_name):
    ignore_folders = ["config", "fixtures", "public", "templates", "tests", "translations", "__pycache__", "www",
                      "docs"]
    list_with_modules = [folder for folder in os.listdir(frappe.get_app_path(app_name)) if
                         folder not in ignore_folders and os.path.isdir(frappe.get_app_path(app_name, folder))]
    list_with_modules = [folder for folder in list_with_modules if
                         "doctype" in os.listdir(frappe.get_app_path(app_name, folder))]
    if isinstance(list_with_modules, str):
        list_with_modules = list_with_modules.split()
    return list_with_modules


def add_uml(app_name, path, extension="png", list_with_modules=None, doctype=None):
    """Add uml diagramm for app"""
    if list_with_modules is None:
        list_with_modules = []

    if not list_with_modules:
        list_with_modules = get_all_modules(app_name)

    list_with_json_files = get_json_from_app(app_name, list_with_modules)

    dot = Digraph(comment="Doctype UML")
    for file in list_with_json_files:
        with open(file, "r") as file:
            json_dump = json.loads(file.read())
            if doctype is not None:
                if json_dump['name'] != doctype:
                    continue
            dot = create_dot(json_dump, dot)
    dot.render(path.split('.')[0], format=extension)


def get_json_from_app(app_name, list_with_modules):
    list_with_json_files = []
    for module in list_with_modules:
        doctype_folder_path = frappe.get_app_path(app_name, module, 'doctype')
        for folder, garbage, files in os.walk(doctype_folder_path):
            if '__pycache__' not in folder and os.path.basename(folder) not in ('doctype', 'templates'):
                if os.path.exists(os.path.join(folder, os.path.basename(folder) + '.json')):
                    list_with_json_files.append(
                        os.path.join(folder, os.path.basename(folder) + '.json'))
    return list_with_json_files
