# Necessary imports
import os
import jinja2

# Set jinja2 template directory
template_dir = os.path.join(os.path.dirname(__file__), '../../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# function for rendering templates
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
