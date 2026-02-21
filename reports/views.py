from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.process_report import process_report
from django.conf import settings
from django.views.generic import TemplateView
import os
import traceback


class HomeView(TemplateView):
    template_name = 'reports/home.html'

    def post(self, request, *args, **kwargs):
        context = {}
        if request.FILES.get('report_file'):
            uploaded_file = request.FILES['report_file']
            print(f"\n{'='*50}")
            print(f"[UPLOAD] File received: {uploaded_file.name}")
            print(f"{'='*50}")

            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            print(f"[UPLOAD] Saved to: {uploaded_file_path}")

            try:
                results = process_report(uploaded_file_path)
                print(f"[RESULT] Raw text (first 300 chars): {results.get('raw_text','')[:300]}")
                print(f"[RESULT] Values found: {results.get('values')}")
                print(f"[RESULT] Statuses: {results.get('statuses')}")
                context['results'] = results
                context['file_url'] = fs.url(filename)
                if not results.get('values'):
                    context['debug_text'] = results.get('raw_text', 'No text extracted.')[:500]
            except Exception as e:
                traceback.print_exc()
                context['error'] = f"Error processing file: {str(e)}"

            print(f"[CONTEXT] Keys set: {list(context.keys())}")

        return render(request, self.template_name, context)

class ReportHistoryView(TemplateView):
    """Render a single history file in the main panel (image/pdf/text)."""

    template_name = 'reports/report_history.html'

    def get(self, request, fname, *args, **kwargs):
        media_dir = settings.MEDIA_ROOT
        safe_path = os.path.join(media_dir, fname)
        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
            return render(request, self.template_name, {'error': 'File not found.', 'file': None})

        url = settings.MEDIA_URL + fname
        # decide how to display based on extension
        ext = os.path.splitext(fname)[1].lower()
        kind = 'other'
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.jfif']:
            kind = 'image'
        elif ext == '.pdf':
            kind = 'pdf'
        elif ext in ['.txt']:
            kind = 'text'

        # Process the file so the history view shows the same Analysis Results
        context = {}
        try:
            results = process_report(safe_path)
            context['results'] = results
            context['file_url'] = url
            if not results.get('values'):
                context['debug_text'] = results.get('raw_text', 'No text extracted.')[:500]
        except Exception as e:
            traceback.print_exc()
            context['error'] = f"Error processing history file: {str(e)}"

        # keep a `file` entry for templates that may use it
        context['file'] = {'name': fname, 'url': url, 'kind': kind}

        # Render the main home template so Analysis Results are shown
        return render(request, 'reports/home.html', context)

