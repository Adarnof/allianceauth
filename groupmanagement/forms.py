from django import forms
from django.conf import settings
from models import AuthGroup

class AuthGroupAddForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AuthGroupAddForm, self).__init__(*args, **kwargs)

        valid_parents = [] 

        for g in AuthGroup.objects.all():
            if (g.owner == user) or (user in g.admins.all()):
                valid_parents.append(g)
#        self.fields['parent'] = forms.ModelChoiceField(queryset=valid_parents, label"Parent Group")

    group_name = forms.CharField(max_length=254, required=True, label="Group Name")
    group_description = forms.CharField(max_length=254, required=True, label="Description")
    hidden = forms.BooleanField(required=False, initial=False, label="Hidden")
    parent = forms.ModelChoiceField(AuthGroup.objects.all(), label="Parent Group", required=False)
