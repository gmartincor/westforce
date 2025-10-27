from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import json
import csv
import io
import zipfile
from django.apps import apps


@login_required
def export_data(request):
    format_type = request.GET.get('format', 'json')
    
    if format_type == 'excel':
        return export_excel()
    elif format_type == 'csv':
        return export_csv()
    elif format_type == 'zip':
        return export_zip()
    else:
        return export_json()


def export_json():
    data = get_export_data()
    response = HttpResponse(
        json.dumps(data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="westforce_data_{timezone.now().strftime("%Y%m%d")}.json"'
    return response


def export_csv():
    data = get_export_data()
    output = io.StringIO()
    
    for model_name, records in data.items():
        if records:
            writer = csv.DictWriter(output, fieldnames=records[0].keys())
            output.write(f"\n--- {model_name.upper()} ---\n")
            writer.writeheader()
            writer.writerows(records)
            output.write("\n")
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="westforce_data_{timezone.now().strftime("%Y%m%d")}.csv"'
    return response


def export_excel():
    try:
        import pandas as pd
        from io import BytesIO
        
        data = get_export_data()
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for model_name, records in data.items():
                if records:
                    df = pd.DataFrame(records)
                    df.to_excel(writer, sheet_name=model_name[:31], index=False)
        
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="westforce_data_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        return response
    except ImportError:
        return JsonResponse({'error': 'Excel export requires pandas and openpyxl'}, status=400)


def export_zip():
    buffer = io.BytesIO()
    data = get_export_data()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for model_name, records in data.items():
            if records:
                csv_content = io.StringIO()
                writer = csv.DictWriter(csv_content, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)
                
                zip_file.writestr(f"{model_name}.csv", csv_content.getvalue())
        
        json_content = json.dumps(data, indent=2, default=str)
        zip_file.writestr("complete_data.json", json_content)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="westforce_complete_{timezone.now().strftime("%Y%m%d")}.zip"'
    return response


def get_export_data():
    data = {}
    
    try:
        Income = apps.get_model('accounting', 'Income')
        incomes = Income.objects.select_related('business_line').all()
        data['incomes'] = [
            {
                'amount': str(income.amount),
                'date': income.date.isoformat() if income.date else None,
                'service_type': income.service_type,
                'business_line': income.business_line.name if income.business_line else None,
                'client_name': income.client_name,
                'payment_method': income.payment_method,
                'description': income.description,
                'reference_number': income.reference_number,
            }
            for income in incomes
        ]
    except Exception:
        data['incomes'] = []
    
    try:
        Expense = apps.get_model('expenses', 'Expense')
        expenses = Expense.objects.select_related('category').all()
        data['expenses'] = [
            {
                'amount': str(expense.amount),
                'date': expense.date.isoformat() if expense.date else None,
                'category': expense.category.name if expense.category else None,
                'description': expense.description,
                'invoice_number': expense.invoice_number,
                'service_category': expense.service_category,
            }
            for expense in expenses
        ]
    except Exception:
        data['expenses'] = []
    
    try:
        BusinessLine = apps.get_model('business_lines', 'BusinessLine')
        business_lines = BusinessLine.objects.all()
        data['business_lines'] = [
            {
                'name': bl.name,
                'level': bl.level,
                'description': bl.description,
                'location': bl.location,
                'is_active': bl.is_active,
            }
            for bl in business_lines
        ]
    except Exception:
        data['business_lines'] = []
    
    return data
