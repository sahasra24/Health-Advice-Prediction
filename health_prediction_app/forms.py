# forms.py
from django import forms
import csv
import os

class AttributeSelectionForm(forms.Form):
    selected_attributes = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(AttributeSelectionForm, self).__init__(*args, **kwargs)
        
        # Fetch attribute choices from CSV file during initialization
        attribute_choices = self.get_attribute_choices()
        self.fields['selected_attributes'].choices = attribute_choices

    def get_attribute_choices(self):
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        csv_path = os.path.join(static_dir, 'data.csv')
        
        attribute_choices = []
        try:
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                attribute_choices = [(row['Attribute'], row['Attribute']) for row in reader]
        except FileNotFoundError:
            print(f"File not found: {csv_path}")
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")
        
        return attribute_choices