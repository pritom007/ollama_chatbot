def convert_md_to_html(md):
    return markdown.markdown(md)

def convert_html_to_md(html):
    return html2text.html2text(html)