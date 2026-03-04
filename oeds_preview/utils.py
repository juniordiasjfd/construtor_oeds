import bs4
from .latex import html_with_latex_class_2_html_with_mathml


def has_parent_with(tag:bs4.element.Tag, parent_name='em'):
    parents_names = list(x.name for x in tag.parents)
    return parent_name in parents_names
def renomeia_tags_and_apply_mathml(
        soup:bs4.BeautifulSoup, 
        de_para={
            'i':'em', 
            'b':'strong'
            }):
    for old_name in de_para:
        ocorrencias = soup.find_all(old_name)
        for ocor in ocorrencias:
            ocor.name = de_para[old_name]
    ocorrencias = soup.find_all('strong')
    for ocor in ocorrencias:
        if has_parent_with(ocor, 'em'):
            new_em = soup.new_tag('em')
            ocor.insert_before(new_em)
            new_em.append(ocor)
            new_em.name = 'strong'
            ocor.name = 'em'
    soup = html_with_latex_class_2_html_with_mathml(soup)
    return soup