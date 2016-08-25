"""Sphinx configuration."""
import pkg_resources
import sphinx_bootstrap_theme


release = pkg_resources.get_distribution("briefy.common").version
version = release.split('.')

major_version = version[0]
minor_version = version[1]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'

project = u'briefy.common'
copyright = u'2016, Briefy'
author = u'Erico Andrei'

version = u'{}.{}'.format(major_version, minor_version)
release = release

language = 'en'

exclude_patterns = ['_build']
# add_module_names = True
# show_authors = False
pygments_style = 'sphinx'
todo_include_todos = True

html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_static_path = ['_static']
html_theme_options = {
    'navbar_title': project,
    'navbar_site_name': "TOC",
    'navbar_sidebarrel': True,
    'navbar_pagenav': True,
    'navbar_pagenav_name': "Page",
    'globaltoc_depth': 1,
    'globaltoc_includehidden': "true",
    'navbar_class': "navbar navbar-inverse",
    'navbar_fixed_top': "true",
    'source_link_position': "nav",
    'bootswatch_theme': "cosmo",
    'bootstrap_version': "3",
}
