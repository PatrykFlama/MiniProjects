from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList

# Create your views here.
def home(response):
    return render(response, "main/home.html", {})


def index(response, id):
    ls = ToDoList.objects.get(id=id)        # get the object with given id

    if ls in response.user.todolist.all():  # check if this todolist belongs to active user
        if response.method == "POST":
            print(response.POST)                # debug
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    if response.POST.get("c" + str(item.id)) == "clicked":
                        item.complete = True
                    else:
                        item.complete = False
                    item.save()
            
            elif response.POST.get("newItem"):
                text = response.POST.get("newText")

                if len(text) > 2:
                    ls.item_set.create(text=text, complete=False)
                else:
                    print("Invalid")
        
        return render(response, "main/list.html", {"ls":ls})

    return render(response, "main/view.html", {})


def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            todo = ToDoList(name=name)
            todo.save()
            response.user.todolist.add(todo)

        return HttpResponseRedirect("/%i" %todo.id)
    else:
        form = CreateNewList()

    return render(response, "main/create.html", {"form":form})


def view(response):
    return render(response, "main/view.html", {})