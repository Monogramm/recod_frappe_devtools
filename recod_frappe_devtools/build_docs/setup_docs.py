"""Automatically setup docs for a project

Call from command line:

	bench setup-docs app path

"""
from __future__ import unicode_literals, print_function

import os, json, frappe, shutil

import jinja2
from frappe.utils import markdown


# def is_singe_doc(basepath, doctype):
#     if "__" not in doctype:
#         with open(basepath + "/" + doctype + ".json", 'r') as f:
#             data_str = f.read()
#             data = json.loads(data_str)
#             return data['issingle'] == 1
#     return True


class SetupDocs(object):
    def __init__(self, app, target_app):

        self.app = app
        self.target_app = target_app

        frappe.flags.web_pages_folders = ['docs', ]
        frappe.flags.web_pages_apps = [self.app, ]
        self.list_without_app_documentation = ['frappe', 'erpnext']

        self.hooks = frappe.get_hooks(app_name=self.app)
        self.app_title = self.hooks.get("app_title")[0]
        self.setup_app_context()

    def setup_app_context(self):
        self.docs_config = frappe.get_module(self.app + ".config.docs")
        version = get_version(app=self.app)
        self.app_context = {
            "app": frappe._dict({
                "name": self.app,
                "title": self.app_title,
                "description": self.hooks.get("app_description")[0],
                "version": version,
                "publisher": self.hooks.get("app_publisher")[0],
                "icon": self.hooks.get("app_icon")[0],
                "email": self.hooks.get("app_email")[0],
                "source_link": self.docs_config.source_link,
                "license": self.hooks.get("app_license")[0],
                "branch": getattr(self.docs_config, "branch", None) or "develop",
            }),
            "metatags": {
                "description": self.hooks.get("app_description")[0],
            },
            "get_doctype_app": frappe.get_doctype_app
        }

    def get_raw_for_md_file(self, app_title, app_name):
        if not os.path.exists(frappe.get_app_path(app_name, 'www')):
            self.list_without_app_documentation.append(app_name)
        if app_name not in self.list_without_app_documentation:
            return "- [{}]({})\n".format(app_title, "/docs/" + app_name)

    def create_general_doc(self, path_folder):
        hooks = frappe.get_hooks()
        list_with_titles = hooks.get("app_title")
        list_with_apps = hooks.get("app_name")
        raws = list(map(self.get_raw_for_md_file, list_with_titles, list_with_apps))
        raws = [raw for raw in raws if raw]  # Remove all None from list
        str_raws = ''
        for raw in raws:
            str_raws += raw
        with open(path_folder + '/' + 'index.md', 'w') as f:
            f.write('''# Documentation site \nYour instance documentation: \n\n''' + str(str_raws)
                    + '\n# License \n Generated Copyright © 2020 [Monogramm](https://www.monogramm.io)'
                      ' \n This project {} licensed.'''.format(
                self.hooks.get('app_license')[0]))

    def build(self, docs_version):
        """Build templates for docs models and Python API"""
        self.docs_path = frappe.get_app_path(self.target_app, 'www', "docs", self.target_app)
        self.path = os.path.join(self.docs_path, docs_version)
        self.app_context["app"]["docs_version"] = docs_version

        self.app_title = self.hooks.get("app_title")[0]
        self.app_path = frappe.get_app_path(self.app)

        print("Deleting current...")
        shutil.rmtree(self.path, ignore_errors=True)
        os.makedirs(self.path)

        self.make_home_pages()

        self.create_general_doc(frappe.get_app_path(self.target_app, 'www', 'docs'))

        for basepath, folders, files in os.walk(self.app_path):

            # make module home page
            if "/doctype/" not in basepath and "doctype" in folders:
                module = os.path.basename(basepath)

                module_folder = os.path.join(self.models_base_path, module)

                self.make_folder(module_folder,
                                 template="templates/autodoc/module_home.html",
                                 context={"name": module})
                self.update_index_txt(module_folder)

            # make for model files
            if "/doctype/" in basepath:
                parts = basepath.split("/")
                # print parts
                module, doctype = parts[-3], parts[-1]

                if doctype != "boilerplate":
                    self.write_model_file(basepath, module, doctype)

            # standard python module
            if self.is_py_module(basepath, folders, files):
                self.write_modules(basepath, folders, files)

        # self.build_user_docs()
        self.copy_user_assets()
        self.add_sidebars()
        shutil.copy(os.path.join(self.docs_path, "_sidebar.json"), os.path.join(self.docs_path, ".."))
        self.add_breadcrumbs_for_user_pages()

    def add_breadcrumbs_for_user_pages(self):
        for basepath, folders, files in os.walk(os.path.join(self.docs_path,
                                                             'user')):  # pylint: disable=unused-variable
            for fname in files:
                if fname.endswith('.md') or fname.endswith('.html'):
                    add_breadcrumbs_tag(os.path.join(basepath, fname))

    def add_sidebars(self):
        '''Add _sidebar.json in each folder in docs'''
        for basepath, folders, files in os.walk(self.docs_path):  # pylint: disable=unused-variable
            with open(os.path.join(basepath, '_sidebar.json'), 'w') as sidebarfile:
                sidebarfile.write(frappe.as_json([
                    {"title": "Search Docs ...", "type": "input", "route": "/search_docs"},
                    {"title": "Docs Home", "route": "/docs/{}".format(self.target_app)},
                    {"title": "{} - User Guide".format(self.app_context['app'].get("title")),
                     "route": "/docs/{}/user".format(self.target_app)},
                    {"title": "{} - Server API".format(self.app_context['app'].get("title")),
                     "route": "/docs/{}/current/api".format(self.target_app)},
                    {"title": "{} - Models (Reference)".format(self.app_context['app'].get("title")),
                     "route": "/docs/{}/current/models".format(self.target_app)},
                    {"title": "{} - Improve Docs".format(self.app_context['app'].get("title")), "route":
                        "{0}/tree/develop/{1}/docs".format(self.docs_config.source_link, self.app)}
                ]))

    def copy_user_assets(self):
        '''Copy docs/user and docs/assets to the target app'''
        print('Copying docs/user and docs/assets...')
        shutil.rmtree(os.path.join(self.docs_path, 'user'),
                      ignore_errors=True)
        shutil.rmtree(os.path.join(self.docs_path, 'assets'),
                      ignore_errors=True)
        shutil.copytree(os.path.join(self.app_path, 'docs', 'user'),
                        os.path.join(self.docs_path, 'user'))
        shutil.copytree(os.path.join(self.app_path, 'docs', 'assets'),
                        frappe.get_app_path(self.target_app, 'www', 'docs', self.target_app, 'assets'))

        # copy index
        shutil.copy(os.path.join(self.app_path, 'docs', 'index.md'),
                    frappe.get_app_path(self.target_app, 'www', 'docs', self.target_app))

    def make_home_pages(self):
        """Make standard home pages for docs, developer docs, api and models
			from templates"""
        # make dev home page
        with open(os.path.join(self.path, "index.html"), "w") as home:
            home.write(frappe.render_template("templates/autodoc/dev_home.html",
                                              self.app_context))

        # make folders
        self.models_base_path = os.path.join(self.path, "models")
        self.make_folder(self.models_base_path,
                         template="templates/autodoc/models_home.html")

        self.api_base_path = os.path.join(self.path, "api")
        self.make_folder(self.api_base_path,
                         template="templates/autodoc/api_home.html")

        # make /user
        user_path = os.path.join(self.docs_path, "user")
        if not os.path.exists(user_path):
            os.makedirs(user_path)

        # make /assets/img
        img_path = os.path.join(self.docs_path, "assets", "img")
        if not os.path.exists(img_path):
            os.makedirs(img_path)

    def build_user_docs(self):
        """Build templates for user docs pages, if missing."""
        # user_docs_path = os.path.join(self.docs_path, "user")

        # license
        with open(os.path.join(self.app_path, "..", "license.txt"), "r") as license_file:
            self.app_context["license_text"] = markdown(license_file.read())
            html = frappe.render_template("templates/autodoc/license.html",
                                          context=self.app_context)

        with open(os.path.join(self.docs_path, "license.html"), "wb") as license_file:
            license_file.write(html.encode("utf-8"))

        # contents
        shutil.copy(os.path.join(frappe.get_app_path("frappe", "templates", "autodoc",
                                                     "contents.html")), os.path.join(self.docs_path, "contents.html"))

        shutil.copy(os.path.join(frappe.get_app_path("frappe", "templates", "autodoc",
                                                     "contents.py")), os.path.join(self.docs_path, "contents.py"))

        # install
        html = frappe.render_template("templates/autodoc/install.md",
                                      context=self.app_context)

        with open(os.path.join(self.docs_path, "install.md"), "w") as f:
            f.write(html)

        self.update_index_txt(self.docs_path)

    def is_py_module(self, basepath, folders, files):
        return "__init__.py" in files \
               and (not "/doctype" in basepath) \
               and (not "/patches" in basepath) \
               and (not "/change_log" in basepath) \
               and (not "/report" in basepath) \
               and (not "/page" in basepath) \
               and (not "/templates" in basepath) \
               and (not "/tests" in basepath) \
               and (not "/docs" in basepath)

    def write_modules(self, basepath, folders, files):
        module_folder = os.path.join(self.api_base_path, os.path.relpath(basepath, self.app_path))
        self.make_folder(module_folder)

        for f in files:
            if f.endswith(".py"):
                full_module_name = os.path.relpath(os.path.join(basepath, f),
                                                   self.app_path)[:-3].replace("/", ".")

                module_name = full_module_name.replace(".__init__", "")

                module_doc_path = os.path.join(module_folder,
                                               self.app + "." + module_name + ".html")

                self.make_folder(basepath)

                if not os.path.exists(module_doc_path):
                    print("Writing " + module_doc_path)
                    with open(module_doc_path, "wb") as f:
                        context = {"name": self.app + "." + module_name}
                        context.update(self.app_context)
                        context['full_module_name'] = self.app + '.' + full_module_name
                        f.write(frappe.render_template("templates/autodoc/pymodule.html",
                                                       context).encode('utf-8'))

        self.update_index_txt(module_folder)

    def make_folder(self, path, template=None, context=None):
        if not template:
            template = "templates/autodoc/package_index.html"

        if not os.path.exists(path):
            os.makedirs(path)

            index_txt_path = os.path.join(path, "index.txt")
            print("Writing " + index_txt_path)
            with open(index_txt_path, "w") as f:
                f.write("")

            index_html_path = os.path.join(path, "index.html")
            if not context:
                name = os.path.basename(path)
                if name == ".":
                    name = self.app
                context = {
                    "title": name
                }
            context.update(self.app_context)
            print("Writing " + index_html_path)
            with open(index_html_path, "w") as f:
                f.write(frappe.render_template(template, context))

    def update_index_txt(self, path):
        index_txt_path = os.path.join(path, "index.txt")
        pages = filter(lambda d: ((d.endswith(".html") or d.endswith(".md")) and d not in ("index.html",)) \
                                 or os.path.isdir(os.path.join(path, d)), os.listdir(path))
        pages = [d.rsplit(".", 1)[0] for d in pages]

        index_parts = []
        if os.path.exists(index_txt_path):
            with open(index_txt_path, "r") as f:
                index_parts = filter(None, f.read().splitlines())

        if not set(pages).issubset(set(index_parts)):
            print("Updating " + index_txt_path)
            with open(index_txt_path, "w") as f:
                f.write("\n".join(pages))

    def write_model_file(self, basepath, module, doctype):
        model_path = os.path.join(self.models_base_path, module, doctype + ".html")

        if not os.path.exists(model_path):
            model_json_path = os.path.join(basepath, doctype + ".json")
            if os.path.exists(model_json_path):
                with open(model_json_path, "r") as j:
                    doctype_real_name = json.loads(j.read()).get("name")

                print("Writing " + model_path)

                with open(model_path, "wb") as f:
                    context = {"doctype": doctype_real_name}
                    context.update(self.app_context)
                    f.write(frappe.render_template("templates/autodoc/doctype.html",
                                                   context).encode("utf-8"))


def get_version(app="frappe"):
    try:
        return frappe.get_attr(app + ".__version__")
    except AttributeError:
        return '0.0.1'


edit_link = '''
<div class="page-container">
	<div class="page-content">
	<div class="edit-container text-center">
		<i class="fa fa-smile"></i>
		<a class="text-muted edit" href="{source_link}/blob/{branch}/{app_name}/{target}">
			Improve this page
		</a>
	</div>
	</div>
</div>'''


def add_breadcrumbs_tag(path):
    with open(path, 'r') as f:
        content = frappe.as_unicode(f.read())
    with open(path, 'wb') as f:
        f.write(('<!-- add-breadcrumbs -->\n' + content).encode('utf-8'))
