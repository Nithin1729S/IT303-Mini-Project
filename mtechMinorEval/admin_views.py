from dotenv import load_dotenv
from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from mtechMinorEval.models import  ActivityLog, Faculty, Project, PathAccess, ProjectEvalSummary
from users.models import Student

load_dotenv()

@login_required(login_url='login')
def summary(request):
    "Gives adminstrator the evaluation summary of entire mtech minor it projects and can be run by only logged in users."
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')
    context = {
        'projects': projects,
    }
    return render(request, 'mtechMinorEval/summary.html', context)

@login_required(login_url='login')
def totalEval(request):
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'student__rollno')  
    sort_order = request.GET.get('order', 'asc') 
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column 

    "Gives adminstrator the evaluation summary of entire mtech minor it projects and can be run by only logged in users."
    projects = ProjectEvalSummary.objects.filter(
                              Q(project__title__icontains=search_query) |
                              Q(student__name__icontains=search_query) |
                              Q(student__rollno__icontains=search_query)
    ).order_by(order_by)
    
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/totalEval.html', context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def adminPanel(request):
    # Check if data is already cached
    path_accesses = cache.get('path_accesses')
    if not path_accesses:
        path_accesses = PathAccess.objects.order_by('-access_count')[:8]
        # Cache the path_accesses data for 5 minutes
        cache.set('path_accesses', path_accesses, timeout=300)  # timeout in seconds
    
    total_visits = sum(access.access_count for access in path_accesses)
    total_bounces = sum(access.bounces for access in path_accesses)
    bounce_rate = (total_bounces / total_visits) * 100 if total_visits > 0 else 0

    # Cache projects, students, and faculties
    projects = cache.get('projects')
    if not projects:
        projects = Project.objects.all()
        cache.set('projects', projects, timeout=3600)

    students = cache.get('students')
    if not students:
        students = Student.objects.all()
        cache.set('students', students, timeout=3600)

    facultys = cache.get('facultys')
    if not facultys:
        facultys = Faculty.objects.all()
        cache.set('facultys', facultys, timeout=3600)

    context = {
        'projects': projects,
        'students': students,
        'facultys': facultys,
        'path_accesses': path_accesses,
        'bounce_rate': bounce_rate,
    }
    
    return render(request, 'mtechMinorEval/adminPanel.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def projectAllotment(request):
    "View the projects database."
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'title')  
    sort_order = request.GET.get('order', 'asc')  

    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

   
    projects= Project.objects.filter(
            Q(title__icontains=search_query) |
            Q(desc__icontains=search_query) |
            Q(student__name__icontains=search_query) |
            Q(student__rollno__icontains=search_query) 
        ).order_by(order_by)

    
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/projectAllotment.html', context)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def studentDatabase(request):
    "View the student database."
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  # Default to 5 entries per page
    sort_column = request.GET.get('sort', 'name')  # Default sort column is 'name'
    sort_order = request.GET.get('order', 'asc')   # Default order is ascending

    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

    # Filter students based on the search query
   
    students = Student.objects.filter(
            Q(rollno__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
    ).order_by(order_by)

    # Pagination
    paginator = Paginator(students, per_page)  # Use the per_page value
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/studentDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def facultyDatabase(request):
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)
    sort_column = request.GET.get('sort', 'name')  # Default sort column is 'name'
    sort_order = request.GET.get('order', 'asc')   # Default order is ascending

    # Determine the order by adding a minus sign for descending order
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

    # Filter facultys based on the search query
    facultys = Faculty.objects.filter(
        Q(name__icontains=search_query) |
        Q(email__icontains=search_query)
    ).order_by(order_by)

    # Pagination
    paginator = Paginator(facultys, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'facultys': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/facultyDatabase.html', context)

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def access_count_view(request):
    path_accesses = PathAccess.objects.all()
    
    total_visits = sum(access.access_count for access in path_accesses)
    total_bounces = sum(access.bounces for access in path_accesses)

    # Calculate bounce rate
    bounce_rate = (total_bounces / total_visits) * 100 if total_visits > 0 else 0

    context = {
        'path_accesses': path_accesses,
        'bounce_rate': bounce_rate,
    }
    return render(request, 'mtechMinorEval/access_count.html', context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def activity_log(request):
    logs=ActivityLog.objects.all().order_by('-timestamp')
    context={
        'logs':logs
    }
    return render(request,'mtechMinorEval/activity_log.html',context)