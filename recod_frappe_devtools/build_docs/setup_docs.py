"""
Automatically setup docs for a project.

Call from command line: bench build-app-docs app path
"""
from __future__ import unicode_literals, print_function

import os, json, frappe, shutil

from recod_frappe_devtools.commands import add_uml
from recod_frappe_devtools.utils import autodoc


def is_py_module(basepath, folders, files):
    return "__init__.py" in files \
           and (not "/doctype" in basepath) \
           and (not "/patches" in basepath) \
           and (not "/change_log" in basepath) \
           and (not "/report" in basepath) \
           and (not "/page" in basepath) \
           and (not "/templates" in basepath) \
           and (not "/tests" in basepath) \
           and (not "/docs" in basepath)


def update_index_txt(path):
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


class SetupDocs(object):
    def __init__(self, app, target_app, extension):
        """Consctuctor for SetupDocs. Init all necessary variables for generating docs."""
        self.list_sidebar = []
        self.app = app
        self.target_app = target_app

        frappe.flags.web_pages_folders = ['docs', ]
        frappe.flags.web_pages_apps = [self.app, ]

        self.hooks = frappe.get_hooks(app_name=self.app)
        self.app_title = self.hooks.get("app_title")[0]

        with open(frappe.get_app_path('recod_frappe_devtools', 'docs', 'docs_apps.txt'), 'r') as f:
            self.list_with_app_docs = f.read().split('\n')

        self.docs_config = frappe.get_module(self.app + ".config.docs")
        version = get_version(app=self.app)
        self.app_list = []
        for app in self.list_with_app_docs:
            if app:
                self.app_list.append(
                    {'app_name': app, 'app_title': frappe.get_hooks(app_name=app)['app_title'][0]})

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
            "get_doctype_app": frappe.get_doctype_app,
            'app_list': self.app_list,
            'extension': extension,
            'version_of_app': autodoc.get_version(self.app),
            'm': autodoc.automodule(self.app)
        }
        self.extension = extension

        self.autodoc_path = frappe.get_app_path('recod_frappe_devtools', 'templates', 'autodoc')
        self.www_docs_path = frappe.get_app_path(target_app, 'www', 'docs')

    def create_general_doc(self):
        """Create docs general home page."""
        self.render_autodoc('docs_home.md', os.path.join(self.www_docs_path, 'index.md'),
                            context={'extension': self.extension})

        # Build the list of links to apps with docs
        for app in self.app_list:
            self.list_sidebar.append({'route': '/docs/{}'.format(app['app_name']), 'title': app['app_title']})

        # Write the sidebar links for docs home
        for app in self.app_list:
            with open(frappe.get_app_path(app['app_name'], 'www', 'docs', "_sidebar.json"), 'w') as f:
                f.write(json.dumps(self.list_sidebar))

    def build(self, docs_version):
        """Build templates for docs models and Python API."""
        with open(frappe.get_app_path('recod_frappe_devtools', 'docs', 'docs_apps.txt'), 'a+') as f:
            if self.app not in self.list_with_app_docs:
                f.write(self.app + '\n')

        self.docs_path = frappe.get_app_path(self.target_app, 'www', "docs", self.target_app)

        self.path = os.path.join(self.docs_path, docs_version)
        self.app_context["app"]["docs_version"] = docs_version

        self.app_path = frappe.get_app_path(self.app)

        print("Deleting current...")
        shutil.rmtree(self.path, ignore_errors=True)
        os.makedirs(self.path)

        self.make_home_pages()

        self.create_general_doc()

        for basepath, folders, files in os.walk(self.app_path):

            # make module home page
            if "/doctype/" not in basepath and "doctype" in folders:
                module = os.path.basename(basepath)
                module_folder = os.path.join(self.models_base_path, module)
                self.make_folder(module_folder,
                                 template="templates/autodoc/module_home.html",
                                 context={"name": module})
                self.render_autodoc("module_home.html", os.path.join(self.models_base_path, module, 'index.html'),
                                    context={"name": module})
                update_index_txt(module_folder)

            # make for model files
            if "/doctype/" in basepath:
                parts = basepath.split("/")
                # print parts
                module, doctype = parts[-3], parts[-1]
                if doctype != "boilerplate":
                    self.write_model_file(basepath, module, doctype)

            # standard python module
            if is_py_module(basepath, folders, files):
                self.write_modules(basepath, folders, files)

        self.copy_user_assets()
        self.add_sidebars()
        self.add_breadcrumbs_for_user_pages()

    def add_breadcrumbs_for_user_pages(self):
        """Add breadcrumbs for user pages in the end of file."""
        for basepath, folders, files in os.walk(
                os.path.join(self.docs_path, 'user')):  # pylint: disable=unused-variable
            print('List with folders: ' + str(folders))
            for fname in files:
                if fname.endswith('.md') or fname.endswith('.html'):
                    add_breadcrumbs_tag(os.path.join(basepath, fname))

    def add_sidebars(self):
        """Add _sidebar.json in each folder in docs."""
        for basepath, folders, files in os.walk(self.docs_path):  # pylint: disable=unused-variable
            with open(os.path.join(basepath, '_sidebar.json'), 'w') as sidebarfile:
                sidebarfile.write(frappe.as_json([
                    {"title": "Search Docs ...", "type": "input", "route": "/search_docs"},
                    {"title": "Docs Home", "route": "/docs"},
                    {"title": "{} - Docs Home".format(self.app_context['app'].get("title")),
                     "route": "/docs/{}".format(self.target_app)},
                    {"title": "{} - User Guide".format(self.app_context['app'].get("title")),
                     "route": "/docs/{}/user".format(self.target_app)},
                    {"title": "{} - Server API".format(self.app_context['app'].get("title")),
                     "route": "/docs/{0}/{1}/api".format(self.target_app, self.app_context["app"].get("docs_version"))},
                    {"title": "{} - Models (Reference)".format(self.app_context['app'].get("title")),
                     "route": "/docs/{0}/{1}/models".format(self.target_app,
                                                            self.app_context["app"].get("docs_version"))},
                    {"title": "{} - Improve Docs".format(self.app_context['app'].get("title")), "route":
                        "{0}/tree/{1}/{2}/docs".format(self.docs_config.source_link,
                                                       self.app_context["app"].get("branch"), self.app)}

                ]))

    def copy_user_assets(self):
        """Copy docs/user and docs/assets to the target app."""
        print('Copying docs/user and docs/assets...')
        shutil.rmtree(os.path.join(self.docs_path, 'user'),
                      ignore_errors=True)
        shutil.rmtree(os.path.join(self.docs_path, 'assets'),
                      ignore_errors=True)

        # copy user guide if exists
        app_user_docs = os.path.join(self.app_path, 'docs', 'user')
        if os.path.exists(app_user_docs):
            shutil.copytree(app_user_docs,
                            os.path.join(self.docs_path, 'user'))

        # copy assets if exists
        app_assets_docs = os.path.join(self.app_path, 'docs', 'assets')
        if os.path.exists(app_assets_docs):
            shutil.copytree(app_assets_docs,
                            frappe.get_app_path(self.target_app, 'www', 'docs', self.target_app, 'assets'))

        # copy index if exists
        app_index_docs = os.path.join(self.app_path, 'docs', 'index.md')
        if os.path.exists(app_index_docs):
            shutil.copy(app_index_docs,
                        frappe.get_app_path(self.target_app, 'www', 'docs', self.target_app))

    def make_home_pages(self):
        """Make standard home pages for docs, developer docs, api and models from templates."""
        # make dev home page
        with open(os.path.join(self.path, "index.html"), "w") as home:
            home.write(frappe.render_template("templates/autodoc/dev_home.html",
                                              self.app_context))

        # make folders
        self.models_base_path = os.path.join(self.path, "models")
        self.make_folder(self.models_base_path,
                         template="templates/autodoc/models_home.html")

        self.render_autodoc('models_home.html',
                            os.path.join(os.path.join(self.www_docs_path, self.app), "current", "models", "index.html"))

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

    def write_modules(self, basepath, folders, files):
        module_folder = os.path.join(self.api_base_path, os.path.relpath(basepath, self.app_path))
        self.make_folder(module_folder)

        for f in files:
            if not f.endswith(".py"):
                continue
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

        update_index_txt(module_folder)

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

    def write_model_file(self, basepath, module, doctype):
        """Write model file."""
        doc_uml_path = self.app + "_{}_uml.{}".format(frappe.scrub(doctype), self.extension)

        model_path = os.path.join(self.models_base_path, module, doctype + ".html")
        if not os.path.exists(model_path):
            model_json_path = os.path.join(basepath, doctype + ".json")
            if os.path.exists(model_json_path):
                print("Writing " + model_path)
                self.app_context.update({'doctype': frappe.unscrub(doctype)})
                context = self.app_context
                context.update({'doc_uml_path': doc_uml_path, 'extension': self.extension})
                self.render_autodoc('doctype.html', model_path, context)

    def add_uml_in_doc(self):
        """Generate uml diagrams for doctype, module and application and move content to assets folder."""
        # Generate umls for all doctypes
        doctypes = frappe.get_all("DocType", {'module': self.app_context['app'].get('title')})
        for doctype in doctypes:
            scrub_doc_name = frappe.scrub(doctype['name'])

            # Path to doctype image file in assets
            doc_path = frappe.get_app_path(self.target_app, 'www', 'docs', self.app, "assets",
                                           self.app + "_{}_uml.{}").format(
                scrub_doc_name, self.extension)

            add_uml(self.app, doc_path, doctype=doctype['name'], extension=self.extension)

        # Generate uml for modules
        list_with_modules = [d for d in os.listdir(self.models_base_path) if
                             os.path.isdir(os.path.join(self.models_base_path, d))]
        for module in list_with_modules:
            module_path = frappe.get_app_path(self.target_app, 'www', 'docs', self.app, "assets",
                                              self.app + "module_uml.{}").format(self.extension)
        add_uml(self.app, module_path, list_with_modules=[module], extension=self.extension)

        # Generate uml for app
        path_to_app_uml = frappe.get_app_path(self.target_app, 'www', 'docs', self.app, "assets", self.app + "_uml")
        add_uml(self.app, path_to_app_uml, extension=self.extension)

    def update_sidebars_in_all_apps(self):
        """Update file _sidebars.json from all apps."""
        list_apps = frappe.get_installed_apps()
        for app in list_apps:
            if app in self.list_with_app_docs:
                with open(frappe.get_app_path(app, "www", "docs", "_sidebar.json"), "w") as file:
                    file.write(json.dumps(self.list_sidebar))

    def render_autodoc(self, template, doc_path, context=None):
        """Render doc from templates folder."""
        if context:
            context.update(self.app_context)
        else:
            context = self.app_context
        with open(os.path.join(self.autodoc_path, template), 'r') as f:
            content = frappe.render_template(f.read(), context=context)
        with open(doc_path, 'w') as f:
            f.write(content)


def get_version(app="frappe"):
    """Get current version of app."""
    try:
        return frappe.get_attr(app + ".__version__")
    except AttributeError:
        return '0.0.1'


def add_breadcrumbs_tag(path):
    """Add breadcrumbs tag in the end of file."""
    with open(path, 'r') as f:
        content = frappe.as_unicode(f.read())
    with open(path, 'wb') as f:
        f.write(('<!-- add-breadcrumbs -->\n' + content).encode('utf-8'))
