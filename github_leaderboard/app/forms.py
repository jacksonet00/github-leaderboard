from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Submit
from django import forms

from github_leaderboard.app.models import Leaderboard


class CreateLeaderboardForm(forms.ModelForm):
    """ Form used on website to create a leaderboard """

    # If true, owner is added to leaderboard on creation
    add_owner = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Leaderboard
        fields = ("name", "repo_url", "end", "start")

    COL_STYLE = "form-group mb-0 mx-auto"
    FIELD_STYLE = "text-center"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(Field("name", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE),
            Column(
                Field("repo_url", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE
            ),
            Column(Field("end", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE),
            Column(
                Field("start", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE
            ),
            Column(
                Field("add_owner", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE
            ),
        )
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Create Leaderboard"))


class ManageLeaderboardForm(forms.Form):
    """Form used on website to manage and change
    values of a leaderboard
    """

    class Meta:
        model = Leaderboard
        fields = ("name", "repo_url", "end", "start")

    name = forms.CharField(required=False, max_length=255)
    repo_url = forms.URLField(required=False)
    start = forms.DateTimeField(required=False)
    end = forms.DateTimeField(required=False)

    COL_STYLE = "form-group mb-0 mx-auto"
    FIELD_STYLE = "text-center"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(Field("name", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE),
            Column(
                Field("repo_url", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE
            ),
            Column(Field("end", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE),
            Column(
                Field("start", css_class=self.FIELD_STYLE), css_class=self.COL_STYLE
            ),
        )
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Change Leaderboard"))
