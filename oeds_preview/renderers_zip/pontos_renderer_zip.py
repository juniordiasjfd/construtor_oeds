from django.template.loader import render_to_string
import bs4
import io
import zipfile
import os
from django.http import HttpResponse
import datetime
from construtor_oeds import settings


def zip_pontos(context, template, oed):
    # 2. Renderizar o HTML
    html_content = render_to_string(template, context)
    html_content = html_content.replace('/static/oeds_preview/', '../resources/')
    html_content = html_content.replace('/media/oeds/', '../resources/')
    soup = bs4.BeautifulSoup(html_content, 'lxml')
    # retirada do botão
    botao_zip = soup.find(attrs={'class':'btn-primary'})
    if botao_zip:
        botao_zip.decompose()
    botao_pdf = soup.find(attrs={'class':'btn-secondary'})
    if botao_pdf:
        botao_pdf.decompose()
    # filtrando as imagens
    lista_de_imagens = list(os.path.basename(x['href']) for x in soup.find_all(attrs={'href':True}))
    lista_de_imagens += list(os.path.basename(x['src']) for x in soup.find_all(attrs={'src':True}))
    lista_de_imagens += ['ico_acessibilidade.svg']
    html_content = str(soup)

    # 3. Criar o arquivo ZIP em memória
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Adicionar o arquivo HTML principal
        zip_file.writestr(f'content/{oed.retranca}.xhtml', html_content)

        # 4. Adicionar Arquivos Estáticos (Styles, Fonts, Images do Static)
        # Define os caminhos das pastas dentro do seu app oeds_preview
        static_root = os.path.join(settings.BASE_DIR, 'oeds_preview', 'static', 'oeds_preview')
        
        folders_to_include = ['styles', 'fonts', 'images']
        
        for folder in folders_to_include:
            folder_path = os.path.join(static_root, folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        # Cria o caminho relativo dentro do ZIP (ex: styles/arquivo.css)
                        rel_path = os.path.relpath(file_full_path, static_root)
                        if folder == 'images':
                            if os.path.basename(rel_path) not in lista_de_imagens:
                                continue
                        zip_file.write(file_full_path, os.path.join('resources', rel_path))

        # 5. Adicionar Imagens de Media (Uploads do Banco de Dados)
        # Aqui você deve decidir se quer manter a estrutura original ou mover para images/
        if oed.imagem_principal:
            zip_file.write(oed.imagem_principal.path, f"resources/images/{os.path.basename(oed.imagem_principal.path)}")
        
        for ponto in oed.pontos.all():
            if ponto.imagem_do_ponto:
                zip_file.write(ponto.imagem_do_ponto.path, f"resources/images/{os.path.basename(ponto.imagem_do_ponto.path)}")

    # 6. Retornar o ZIP como resposta de download
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    hora = format(datetime.datetime.now(), '%Y-%m-%d_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="{oed.retranca}_export_{hora}.zip"'
    return response