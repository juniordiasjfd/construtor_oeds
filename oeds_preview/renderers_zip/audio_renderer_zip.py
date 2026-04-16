from django.template.loader import render_to_string
import bs4
import io
import zipfile
import os
from django.http import HttpResponse
from construtor_oeds import settings


def zip_audio(context, template, oed):

    html_content = render_to_string(template, context)
    html_content = html_content.replace('/static/oeds_preview/', '../resources/')
    html_content = html_content.replace('/media/oeds/', '../resources/')

    soup = bs4.BeautifulSoup(html_content, "lxml")

    # remove botões de interface
    for btn in soup.find_all(attrs={"class": "btn"}):
        btn.decompose()
    
    # filtrando as imagens
    lista_de_imagens = list(os.path.basename(x['href']) for x in soup.find_all(attrs={'href':True}))
    lista_de_imagens += list(os.path.basename(x['src']) for x in soup.find_all(attrs={'src':True}))
    lista_de_imagens += ['ico_acessibilidade.svg']

    html_content = str(soup)

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        # XHTML
        zip_file.writestr(
            f"content/{oed.retranca}.xhtml",
            html_content
        )

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

        # MP3
        audio_path = oed.audio.arquivo_do_audio.path
        zip_file.write(
            audio_path,
            f"resources/audios/{os.path.basename(audio_path)}"
        )

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")

    response["Content-Disposition"] = (
        f'attachment; filename="{oed.retranca}.zip"'
    )

    return response