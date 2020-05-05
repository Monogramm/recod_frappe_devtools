from __future__ import unicode_literals, absolute_import

import os

import plantuml


def create_file_from_plant_uml_file(path_to_uml_syntax_file, path_to_png=None):
    plant_uml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")
    plant_uml.processes_file(path_to_uml_syntax_file, outfile=path_to_png)


def process_uml_syntax(path_to_doctype_directory):
    """
    Create file with plantUML syntax
    :param path_to_doctype_directory:
    :return:
    """
    print("Realization")