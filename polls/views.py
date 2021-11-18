"""View for the Django poll."""
# from datetime import timedelta
# from django import template
from django.shortcuts import get_object_or_404, render, get_list_or_404
# from django.http import HttpResponse, response, Http404, HttpResponseRedirect
from django.http import HttpResponseRedirect
from .models import Question, Choice, Vote
# from django.template import context, loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
# from django.test import TestCase
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class IndexView(generic.ListView):
    """The poll page index."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return index queryset."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """The poll page detail."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Return detail queryset."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """The poll page result."""

    model = Question
    template_name = 'polls/results.html'


def index(request):
    """Poll index."""
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """Poll detail."""
    question = get_list_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """Poll result."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def get_vote_for_user(user, poll_question):
    """Find and return an existing vote for a user on a poll.

    Returns:
        The user's Vote or None if no vote for this poll_question
    """
    votes = Vote.objects.filter(user=user)\
                .filter(choice__question=poll_question)
    # should be at most one Vote
    if votes.count() == 0:
        return None
    else:
        return votes[0]


@login_required
def vote(request, question_id):
    """Poll vote."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.warning(request, "You didn't select a choice.")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    else:
        if question.end_date < timezone.now():
            messages.error(request, "You voted failed! Polls have ended.")
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        # selected_choice.votes += 1
        # selected_choice.save()
        
        # get previous vote from user
        user = request.user
        vote = get_vote_for_user(user, question)
        # case 1: user has not voted for this poll question yet
        # Create a new vote object
        if not vote:
            vote = Vote(user=user, choice=selected_choice)
        else:
            # case 2: user has already vote
            # Modify the existing vote and save it
            vote.choice = selected_choice
        vote.save()

        messages.success(request, "You voted successfully.")
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
