from dependencies import pdfkit,jinja2

class PDFGenerator:
    def __init__(self, path='./'):
        self.path = path
        template_loader = jinja2.FileSystemLoader(searchpath=self.path)
        self.template_env = jinja2.Environment(loader=template_loader)

    def set_template(self, template_path):
        self.template = self.template_env.get_template(template_path)

    def generate(self, data, pdf_path):
        # generate pdf
        html = self.template.render(data)
        return pdfkit.from_string(html, pdf_path)