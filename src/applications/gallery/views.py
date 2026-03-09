from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from .models import Gallery
from .forms import GalleryForm
# Create your views here.


def gallery_list(request):
    content = Gallery.objects.order_by('-published_at')
    return render(request, 'gallery/gallery_list.html', {'content': content})

def gallery_detail(request, pk):
    content = get_object_or_404(Gallery, pk=pk)
    return render(request, 'gallery/gallery_detail.html', {'content': content})

@login_required
@permission_required('gallery.add_gallery', raise_exception=True)
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = GalleryForm()
    return render(request, 'gallery/gallery_form.html', {'form': form})
