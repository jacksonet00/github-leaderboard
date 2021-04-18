import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from github import GithubException

from datetime import datetime, timedelta

from github_leaderboard.app.forms import CreateLeaderboardForm, ManageLeaderboardForm
from github_leaderboard.app.models import Leaderboard
from django.db.models import Count

import random


from . import methods, models, scheduled_tasks

if settings.AUTO_UPDATE_LEADERBOARD:
    scheduled_tasks.LEADERBOARD_UPDATE_THREAD.start()

User = get_user_model()
logger = logging.getLogger(__name__)


class FetchLeaderboardCommitsView(View):
    """ preserve Order of application of Decorators. """

    @method_decorator(login_required)
    # @method_decorator(decorators.admin_only) # This will only allow admins to access this method
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        if leaderboard.closed:
            messages.error(self.request, "Leaderboard is closed. operation aborted.")
            return redirect("leaderboard", id=id)

        try:
            updates = methods.refresh_leaderboard_commits(id)
            messages.success(self.request, str(updates["new"]) + " records updated")
            return redirect("leaderboard", id=id)
        except GithubException as e:
            messages.error(
                self.request, "Error: " + str(e.status) + ", " + str(e.data["message"])
            )
            return redirect("leaderboard", id=id)


@method_decorator(login_required, name="dispatch")
class LeaderboardView(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        entries = leaderboard.get_ranked_user_commit_data()
        
        data_chart1 = []
        labels_chart1 = []

        datasets = {}

        for entry in entries:
            # generate randor color for dataset (for chart2)
            random_value = lambda: random.randint(0,255)
            color = '#%02X%02X%02X' % (random_value(),random_value(),random_value())

            # Prepare labels and data for chart1
            labels_chart1.append(entry["user"])
            data_chart1.append(entry["total"])

            # initialize dataset for chart2
            datasets[entry["user"]] = {
                "label":entry["user"],
                "data":[],
                "backgroundColor":color,
            }
        

        user_set = set(
            entity[0]
            for entity in leaderboard.participants.all().values_list("github_username")
        )

        data_chart2 = []
        labels_chart2 = []

        # iterate over all days between start and end of leaderboard
        for date in methods.daterange(leaderboard.start, leaderboard.end):
            labels_chart2.append( str(date.date()))

            # get only those commits which are made at current date
            commits = models.Commit.objects.filter(leaderboard=leaderboard, timestamp=date.date(), user__in=user_set )
            count = commits.values('user').annotate(total=Count("user"))

            # append those users's commit count who have made commits at current date
            for entry in count:
                datasets[entry["user"]]['data'].append(entry['total'])

            # append those users's commit count who do not have made any commits at current date
            for user in user_set.difference(set(entity["user"] for entity in count)):
                datasets[entry["user"]]['data'].append(0)
        
        context = {
            "leaderboard": leaderboard,
            "entries": entries,
            
            "data_chart1": data_chart1,
            "labels_chart1": labels_chart1,

            "labels_chart2": labels_chart2,
            "datasets": datasets,
        }
        return render(request, "pages/leaderboard.html", context)


@method_decorator(login_required, name="dispatch")
class CloseLeaderboardIfEndedView(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        leaderboard.close_if_ended()
        return redirect("leaderboard", id=id)


@method_decorator(login_required, name="dispatch")
class ManageLeaderboardParticipantsView(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        context = {
            "leaderboard": leaderboard,
        }
        return render(request, "pages/manage_participant.html", context)

    def post(self, request, id):
        username = request.POST["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "user does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except models.Leaderboard.DoesNotExist:
            messages.error(request, "leaderboard does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        if leaderboard.closed:
            messages.error(request, "cant add participant of closed leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        if user in leaderboard.participants.all():
            messages.error(request, "user is already a participant in this leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        leaderboard.participants.add(user)
        messages.success(request, "participant added successfully. ")
        return redirect("manage_leaderboard_participants", id=id)


@method_decorator(login_required, name="dispatch")
class ManageLeaderboardView(View):

    template = "pages/manage_leaderboard.html"

    def get(self, request, id):
        ctx = self.context(id)
        leaderboard = ctx["leaderboard"]
        if request.user != leaderboard.owner:
            return HttpResponseForbidden(render(request, "403.html"))
        else:
            return render(request, self.template, ctx)

    def post(self, request, id):
        ctx = self.context(id)
        leaderboard = ctx["leaderboard"]
        if request.user != leaderboard.owner:
            return HttpResponseForbidden(render(request, "403.html"))
        else:
            form = ManageLeaderboardForm(request.POST)
            if form.is_valid():
                try:
                    if form.cleaned_data["name"]:
                        leaderboard.name = form.cleaned_data["name"]
                    if form.cleaned_data["repo_url"]:
                        # Check if it's a change because this will be expensive
                        if leaderboard.repo_url != form.cleaned_data["repo_url"]:
                            leaderboard.repo_url = form.cleaned_data["repo_url"]
                            try:
                                methods.dump_commits(leaderboard)
                                messages.warning(
                                    request,
                                    """
                                    Commit history was dumped due to repo_url change,
                                    you will want to refresh the leaderboard.
                                    """,
                                )
                            except Exception as e:
                                messages.error(
                                    request,
                                    f"""
                                    Commits from old repo_url were not dumped due
                                    to unexpected error:
                                    {str(e)}
                                    """,
                                )
                    if form.cleaned_data["start"]:
                        leaderboard.start = form.cleaned_data["start"]
                    if form.cleaned_data["end"]:
                        leaderboard.end = form.cleaned_data["end"]
                    leaderboard.save()
                    messages.success(request, "Leaderboard updated successfully!")
                except Exception as e:
                    messages.error(request, f"Unexpected Error Occurred {str(e)}")
                ctx["leaderboard"] = leaderboard  # Pass the updated leaderboard
            else:
                ctx["management_form"] = form  # Pass the form back with errors
            return render(request, self.template, ctx)

    def context(self, id):
        return {
            "management_form": ManageLeaderboardForm,
            "leaderboard": get_object_or_404(models.Leaderboard, id=id),
        }


@method_decorator(login_required, name="dispatch")
class DeleteLeaderboardParticipantsView(View):
    def get(self, request, id, userid):
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            messages.error(request, "user does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except models.Leaderboard.DoesNotExist:
            messages.error(request, "leaderboard does not exists")
            return redirect("manage_leaderboard_participants", id=id)
        if leaderboard.closed:
            messages.error(request, "cant remove participant of closed leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        leaderboard.participants.remove(user)
        messages.success(request, "participant removed successfully. ")
        return redirect("manage_leaderboard_participants", id=id)


def dashboard(request):
    """ View for the dashboard page of the website """
    template = "pages/dashboard.html"
    if not request.user.is_authenticated:
        return HttpResponseForbidden(render(request, "403.html"))
    if request.method == "GET":
        has_linked_github = methods.has_social_token(request.user)
        if not has_linked_github:
            messages.warning(
                request,
                """
                Your account does not have a linked GitHub account.
                It is recommended to link your account,
                otherwise your leaderboards may only be able to refresh infrequently.
                """,
            )
        ctx = dashboard_context(request)
        return render(request, template, context=ctx)
    elif request.method == "POST":
        return dashboard_post(request)
    else:
        raise Http404("HTTP method not defined on this page")


def leaderboard_delete(request, pk=None):
    """Special view for deleting leaderboards from across the site

    kwargs:
        pk -- a leaderboard id (primary key)
    """
    template = "pages/deleteLeaderboard.html"
    if pk is not None and request.user.is_authenticated:
        leaderboard = get_object_or_404(Leaderboard, id=pk)
        if leaderboard.owner == request.user:
            ctx = {}
            success = False
            msg = ""
            if request.method == "POST":
                try:
                    leaderboard.delete()
                except Exception as e:
                    msg = f"An error occured when trying to delete {leaderboard.name}"
                    msg += "\n" + str(e)
                    ctx["message"] = msg
                    prompt = False
                else:
                    success = True
                    prompt = False
            else:
                prompt = True
            ctx = {
                "message": msg,
                "prompt": prompt,
                "success": success,
                "pk": pk,
                "ldb_name": leaderboard.name,
            }
            return render(request, template, context=ctx)
    return HttpResponseForbidden(render(request, "403.html"))


def dashboard_post(request):
    """ Handles POST for dashboard view """
    template = "pages/dashboard.html"
    form = CreateLeaderboardForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        add_owner = data["add_owner"]
        del data["add_owner"]  # Drop the fields not needed by leaderboard model
        ldb = Leaderboard.objects.create(**data, owner=request.user)
        if add_owner:
            ldb.participants.add(request.user)  # Add the creator as participant
        return render(request, template, context=dashboard_context(request))
    else:
        ctx = dashboard_context(request)
        ctx["creation_form"] = form  # Send it back with error messages
        return render(request, template, context=ctx)


def dashboard_context(request):
    """Returns a context dictionary for the dashboard view
    Params:
        request - The HTTP request
    Returns:
        {
            'owned_leaderboards': dict of leaderboards owned by user
            'member_leaderboards': dict of leaderboards user is member of
            'creation_form': the leaderboard creation form
        }
    """
    if request.user.is_authenticated:
        owned_leaderboards = Leaderboard.objects.filter(owner=request.user)
        member_leaderboards = Leaderboard.objects.filter(participants=request.user)
        member_leaderboards = member_leaderboards.difference(
            owned_leaderboards
        )  # Remove duplicate elements
        creation_form = CreateLeaderboardForm()
        context = {
            "owned_leaderboards": owned_leaderboards,
            "member_leaderboards": member_leaderboards,
            "creation_form": creation_form,
        }
        return context
    else:
        raise PermissionDenied


def http501(message):
    """Returns a HTTP Response 501 Not Implemented
    with message as content
    """
    response = HttpResponse(message)
    response.status_code = 501
    return response
