from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.process_report import process_report
import os
import traceback

def home(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('report_file'):
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

    return render(request, 'reports/home.html', context)

