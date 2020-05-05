from __future__ import unicode_literals, absolute_import

import os

import plantuml


def build_uml():
    plant_uml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")
    plant_uml.processes_file(os.path.dirname(__file__) + "/test_file.txt")


