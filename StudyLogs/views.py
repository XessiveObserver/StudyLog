from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

import StudyLogs
from . models import Topic, Entry
from . forms import TopicForm, EntryForm

# Create your views here.

def index(request):
    """Home page for StudyLog."""
    return render(request, 'StudyLogs/index.html')

@login_required
def topics(request):
    """Show all topics."""
    # Restricting access to appropriate users.
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'StudyLogs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all it's entries."""
    topic = Topic.objects.get(id=topic_id)
    # Make sure the topic belongs to the current user.
    if topic.owner != request.user:
        raise Http404

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries':entries}
    return render(request, 'StudyLogs/topic.html', context)

@login_required
def new_topic(request):
    """Add new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # Post data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('StudyLogs:topics')

    # Display blank or invalid form.
    context = {'form': form}
    return render(request, 'StudyLogs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for aparticular topic."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # No data submitted; create a blank form
        form = EntryForm()
    else:
        # Post data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('StudyLogs:topic', topic_id=topic_id)

    # Display blank or invalid form
    context = {'topic': topic, 'form': form}
    return render(request, 'StudyLogs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry
        form = EntryForm(instance=entry)
    else:
        # Post data submitted; process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('StudyLogs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'StudyLogs/edit_entry.html', context)