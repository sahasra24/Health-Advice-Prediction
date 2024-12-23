from django.shortcuts import render, redirect
from .forms import AttributeSelectionForm
import os
import csv
import json
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        return redirect('select_attributes')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('select_attributes')  # Redirect to attribute selection view
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('select_attributes')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('select_attributes')  # Redirect to attribute selection view
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required(login_url='login')
def select_attributes_view(request):
    if request.method == 'POST':
        form = AttributeSelectionForm(request.POST)
        if form.is_valid():
            selected_attributes = form.cleaned_data['selected_attributes']
            averages, advice_results, precautions_results, statement_results = calculate_attribute_sums(selected_attributes)
            return render(request, 'result_template.html', {
                'averages': averages,
                'advice_results': advice_results,
                'precautions_results': precautions_results,
                'statement_results': statement_results
            })
    else:
        form = AttributeSelectionForm()
    return render(request, 'form_template.html', {'form': form})

def calculate_attribute_sums(selected_attributes):
    sums = {col: 0 for col in ['Body', 'Cardiac', 'Pulmonary', 'Muscle', 'Immune', 'Renal', 'Hepatic', 'Metabolic', 'Brain']}
    attribute_count = {col: 0 for col in sums}

    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    csv_path = os.path.join(static_dir, 'data.csv')

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Attribute'] in selected_attributes:
                for col in sums:
                    if float(row.get(col, 0)) != 0:
                        attribute_count[col] += 1
                    sums[col] += float(row.get(col, 0))

    averages = {col: sums[col] / attribute_count[col] if attribute_count[col] != 0 else 0 for col in sums}

    advice_path = os.path.join(static_dir, 'advice.json')
    with open(advice_path, 'r') as advice_file:
        advice_data = json.load(advice_file)

    precautions_path = os.path.join(static_dir, 'precautions.json')
    with open(precautions_path, 'r') as precaution_file:
        precautions_data = json.load(precaution_file)

    statements_path = os.path.join(static_dir, 'statements.json')
    with open(statements_path, 'r') as statement_file:
        statements_data = json.load(statement_file)

    advice_results = {}
    precautions_results = {}
    statement_results = {}

    for system_name, health_score in averages.items():
        for advice_block in advice_data['advice']:
            if advice_block['system_name'] == system_name:
                advice_range = advice_block['advice_range']
                if advice_range[0] < health_score <= advice_range[1]:
                    advice_results[system_name] = advice_block['health_advices']

        for precaution_block in precautions_data['precautions']:
            if precaution_block['system_name'] == system_name:
                precaution_range = precaution_block['precaution_range']
                if precaution_range[0] < health_score <= precaution_range[1]:
                    precautions_results[system_name] = precaution_block['precautions_details']

        for statement_block in statements_data['statements']:
            if statement_block['system_name'] == system_name:
                statement_range = statement_block['health_score_range']
                if statement_range[0] < health_score <= statement_range[1]:
                    statement_info = {
                        'quote': statement_block['quote'],
                        'author': statement_block['author'],
                        'statement': statement_block['statement']
                    }
                    statement_results[system_name] = statement_info

    return averages, advice_results, precautions_results, statement_results