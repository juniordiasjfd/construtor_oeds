from django.views.generic import DetailView
from oeds.models import Oed, TipoOed
import bs4
from PIL import Image
from django.utils.safestring import mark_safe
import copy
import io
import zipfile
import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
import datetime
from usuarios.views import CoordenadorRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .latex import html_with_latex_class_2_html_with_mathml
from xhtml2pdf import pisa
from django.urls import reverse
from .renderers.pontos_renderer import render_pontos
from .renderers.audio_renderer import render_audio
from .renderers_zip.pontos_renderer_zip import zip_pontos
from .renderers_zip.audio_renderer_zip import zip_audio


RENDERERS = {
    'renderers': {
            "FAIXA_AUDIO": render_audio,
            "PODCAST": render_audio,
            "PONTO_CLICAVEL": render_pontos,
            "MAPA_CLICAVEL": render_pontos,
        },
    'templates': {
            "FAIXA_AUDIO": 'oeds_preview/preview_audio.xhtml',
            "PODCAST": 'oeds_preview/preview_audio.xhtml',
            "PONTO_CLICAVEL": 'oeds_preview/preview_pontos.xhtml',
            "MAPA_CLICAVEL": 'oeds_preview/preview_pontos.xhtml',
    }
}

class OedPreviewDetailView(DetailView):
    model = Oed
    # template_name = 'oeds_preview/preview.xhtml' # O caminho do seu template específico
    context_object_name = 'oed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motor = self.object.tipo.motor_de_renderizacao
        context.update(RENDERERS['renderers'][motor](self.object))
        return context
    def get_template_names(self):
        motor = self.object.tipo.motor_de_renderizacao
        return RENDERERS['templates'][motor]

class OedDownloadZipView(CoordenadorRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        oed = Oed.objects.get(pk=self.kwargs["pk"])
        motor = oed.tipo.motor_de_renderizacao

        renderer = RENDERERS["renderers"][motor]
        template = RENDERERS["templates"][motor]

        context = {"oed": oed}
        context.update(renderer(oed))

        if motor == "FAIXA_AUDIO":
            return zip_audio(context, template, oed)

        if motor in ["PONTO_CLICAVEL", "MAPA_CLICAVEL"]:
            return zip_pontos(context, template, oed)

class OedDownloadPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 1. Obter o objeto e os dados do contexto (Reutilizando sua lógica existente)
        oed = Oed.objects.get(pk=self.kwargs['pk'])
        preview_view = OedPreviewDetailView()
        preview_view.object = oed
        context = preview_view.get_context_data(object=preview_view.object)
        
        # 2. Renderizar o HTML e limpar com BeautifulSoup
        template_name = preview_view.get_template_names()
        html_string = render_to_string(template_name, context)
        soup = bs4.BeautifulSoup(html_string, 'lxml')
        for fig in soup.find_all('figcaption'):
            fig.name = 'p'
        url_editar = self.request.build_absolute_uri(
            reverse('editar_oed', kwargs={'pk': preview_view.object.pk})
        )
        soup.find('body').insert(0, bs4.BeautifulSoup(f'<p><strong>Acesse para editar:</strong> <a href="{url_editar}">{url_editar}</a></p><p><strong>Retranca:</strong> {preview_view.object.retranca}</p>','html.parser'))

        # Remove CSS e Scripts originais para o PDF ficar limpo
        for s in soup.find_all(['link', 'style', 'script']):
            s.decompose()
        
        # Remove botões de interface
        for btn in soup.find_all(attrs={'class': 'btn'}):
            btn.decompose()

        # Ajuste de caminhos de imagem para o xhtml2pdf encontrar os arquivos no servidor
        for img in soup.find_all('img'):
            if img.get('src') and img['src'].startswith('/media/'):
                # Transforma a URL do browser em caminho de arquivo local
                relative_path = img['src'].replace('/media/', '')
                img['src'] = os.path.join(settings.MEDIA_ROOT, relative_path)

        # 3. Adicionar estilo básico para impressão
        estilo_pdf = soup.new_tag('style')
        estilo_pdf.string = """
            @page { size: a4 portrait; margin: 1cm; }
            body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; }
            h1, h2, h3 { color: #333; margin-top: 15pt; }
            img { max-width: 100%; height: auto; }
            .mapa-popup { border: 0.5pt solid #aaa; padding: 10px; margin-bottom: 20px; }
            .c3idiomabold{font-style:italic;font-weight:bold}.c3idiomaitalico{font-style:italic}.c3idiomabolditalico{font-style:italic;font-weight:bold}.latex{font-family:Courier,monospace}.d3vinheta,.d3vinhetaabertura{font-style:italic;margin:0.5em 0}.d3vinhetaabertura{margin-top:1em}.d3rubricatranscricao,.d3rubricatxad{font-weight:bold}.d3rubricatxad{margin:1em 0 0.4em}.d3txtranscricao{margin:0.4em 0}.d3txtranscanto{font-style:italic;margin:0.5em 0}.d3txad{margin:0.5em 0;font-family:Helvetica,Arial,sans-serif}.d3creditosoed{margin-top:1em}.url_para_encurtar{background-color: lightgreen}
        """
        soup.head.append(estilo_pdf)

        # 4. Gerar o PDF
        html_final = str(soup)
        result = io.BytesIO()
        
        # O pisa.pisaDocument transforma o HTML em PDF
        pdf = pisa.pisaDocument(io.BytesIO(html_final.encode("utf-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{preview_view.object.retranca}_{hora}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        return HttpResponse("Erro técnico ao gerar o PDF.", status=500)



