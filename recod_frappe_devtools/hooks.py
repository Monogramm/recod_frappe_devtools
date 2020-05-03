# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt
"""Configuration for hooks."""

from __future__ import unicode_literals


app_name = "recod_frappe_devtools"
app_title = "Recod Frappe DevTools"
app_publisher = "Monogramm"
app_description = "Frappe application to provide more/better development tools."
app_icon = "octicon octicon-beaker"
app_color = "grey"
app_email = "opensource@monogramm.io"
app_license = "AGPL v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/recod_frappe_devtools/css/recod_frappe_devtools.css"
# app_include_js = "/assets/recod_frappe_devtools/js/recod_frappe_devtools.js"

# include js, css files in header of web template
# web_include_css = "/assets/recod_frappe_devtools/css/recod_frappe_devtools.css"
# web_include_js = "/assets/recod_frappe_devtools/js/recod_frappe_devtools.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "recod_frappe_devtools.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "recod_frappe_devtools.install.before_install"
# after_install = "recod_frappe_devtools.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "recod_frappe_devtools.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"recod_frappe_devtools.tasks.all"
# 	],
# 	"daily": [
# 		"recod_frappe_devtools.tasks.daily"
# 	],
# 	"hourly": [
# 		"recod_frappe_devtools.tasks.hourly"
# 	],
# 	"weekly": [
# 		"recod_frappe_devtools.tasks.weekly"
# 	]
# 	"monthly": [
# 		"recod_frappe_devtools.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "recod_frappe_devtools.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "recod_frappe_devtools.event.get_events"
# }

