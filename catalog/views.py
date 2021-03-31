from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Book, Author, BookInstance, Genre
from django.views import generic
import datetime

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from catalog.forms import RenewBookForm
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

def is_librarian(user):
    return user.groups.filter(name='librarian').exists()

#@user_passes_test(is_librarian)
class LoanedBooksAllListView(LoginRequiredMixin,UserPassesTestMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    
    
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get(self, request, *args, **kwargs):
       # isLibrarian = self.request.user.groups.filter(name='librarian').exists()
        context = {
        #    'islibrarian' : isLibrarian,
        }
       # self.object = self.get_object(queryset=Publisher.objects.all())
        return super().get(request, *args, **kwargs)
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    def test_func(self):
        return self.request.user.groups.filter(name='librarians').exists()

def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorDetailView(generic.DetailView):
    model = Author

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

   # def get_context_data(self, **kwargs):
   ##     # Call the base implementation first to get the context
    #    context = super(BookListView, self).get_context_data(**kwargs)
    #    # Create any data and add it to the context
    #    context['some_data'] = 'This is just some data'
    #    return context




def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})


def author_detail_view(request, primary_key):
    author = get_object_or_404(Author, pk=primary_key)
    return render(request, 'catalog/author_detail.html', context={'book': author})
    
@login_required
def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    if 'num_visits' not in request.session:
        request.session['num_visits'] = 8

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')    

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'summary', 'isbn', 'author_id']
    

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('book')    