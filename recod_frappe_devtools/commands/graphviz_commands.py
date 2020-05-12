from __future__ import unicode_literals, absolute_import

import json
import os

import frappe
from graphviz import Digraph


def create_dot(json_dump, dot):
    label = json_dump['name'] + "|"
    links = []
    for field in json_dump['fields']:
        if field['fieldtype'] not in ("Section Break"):
            label += "{}: {} {}\l".format(field['fieldtype'], field['fieldname'],
                                          "({})".format(field.get('options')) if field.get('options') else "")
        if field['fieldtype'] == 'Link':
            links.append({'head': json_dump['name'], 'end': field['options']})
    label = "{" + label + "}"
    dot.node(json_dump['name'], label, shape="record")
    for link in links:
        dot.edge(link['head'], link['end'])
    return dot


def add_uml(app_name, path):
    list_with_json_files = get_all_json_files_from_app(app_name)
    dot = Digraph(comment='Doctype UML')
    for file in list_with_json_files:
        with open(file, "r") as file:
            json_dump = json.loads(file.read())
            dot = create_dot(json_dump, dot)
    dot.render(path, view=True)


def get_all_json_files_from_app(app_name):
    doctype_folder_path = frappe.get_app_path(app_name, app_name, 'doctype')
    list_with_json_files = []
    for folder, garbage, files in os.walk(doctype_folder_path):
        if '__pycache__' not in folder and os.path.basename(folder) != 'doctype':
            print(folder)
            list_with_json_files.append(
                folder + "/" + os.path.basename(folder) + '.json')
    return list_with_json_files
