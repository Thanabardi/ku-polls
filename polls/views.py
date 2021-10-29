"""The Polls app views."""
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question, Votes
from django.contrib.auth.decorators import login_required


class IndexView(generic.ListView):
    """Return questions in index views."""

    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        """Return published questions. (not including those set to be published in the future)."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:]


class DetailView(generic.DetailView):
    """Return questions in detail views."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:]

        # # also pass the deadline.
        # can_vote_id = []
        # for question in Question.objects.all():
        #     if question.can_vote():
        #         can_vote_id.append(question.id)
        # return Question.objects.filter(id__in=can_vote_id).order_by('-pub_date')[:]


class ResultsView(generic.DetailView):
    """Result view configuration."""

    model = Question
    template_name = 'polls/results.html'


def index(request):
    """Return index view page that contains questions."""
    question_list = Question.objects.order_by('-pub_date')[:]
    context = {'question_list': question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """Return detail view page by question id."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """Return result view page by question id."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


@login_required(login_url='/accounts/login/')
def vote(request, question_id):
    """Return vote view page by question id and after voting redirect to the result page."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        choice_id = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_id)
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        user = request.user
        vote = get_vote_for_user(question, user)

        # case 1: user has not vote for this poll question yet Create Objects
        if not vote:
            vote = Votes(user=user, choice=selected_choice)
        else:
            # case 2: user has already voted. Modify the exist vote and save it.
            vote.choice = selected_choice
        vote.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def get_vote_for_user(question, user):
    """
    Find and return an existing vote for user on a poll question.

    Returns:
        The user vote
    """
    try:
        votes = Votes.objects.filter(user=user).filter(choice__question=question)
        if votes.count() == 0:
            return None
        else:
            return votes[0]
    except Votes.DoesNotExist:
        return None
