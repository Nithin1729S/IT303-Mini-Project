import os
import threading
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from mtechMinorEval.models import  Project
from mtechMinorEval.forms import ExaminerEvaluationForm, GuideEvaluationForm, ProfileEditForm, StudentEditForm
from users.models import Profile,Faculty,Student
from mtechMinorEval.models import GuideEvaluation,ExaminerEvaluation,ProjectEvalSummary
from .tasks import log_activity
load_dotenv()

def home(request):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    return render(request,'mtechMinorEval/home.html',{'faculty':faculty})


@login_required(login_url='login')
def projectsList(request):
    user = request.user
    if user.is_superuser:
        return redirect('admin-panel')

    if user.is_authenticated:
        userEmail = user.email
        userProfile = get_object_or_404(Profile, email=userEmail)

        if userProfile.role == 'faculty':
            faculty = get_object_or_404(Faculty, profile=userProfile)

            # Get search and sorting parameters
            search_query = request.GET.get('search', '')
            per_page = request.GET.get('per_page', 5)
            sort_column = request.GET.get('sort', 'title')
            sort_order = request.GET.get('order', 'asc')

            # Basic query without complex lookups
            projects = Project.objects.filter(
                Q(guide=faculty) | Q(examiner=faculty)
            ).distinct()


            if search_query:
                projects = projects.filter(
                    Q(title__icontains=search_query) | 
                    Q(student__rollno__icontains=search_query) |
                    Q(student__name__icontains=search_query) |
                    Q(student__email__icontains=search_query) 
                )

            # Simple sorting
            if sort_order == 'desc':
                projects = projects.order_by(f'-{sort_column}')
            else:
                projects = projects.order_by(sort_column)

            # Handle pagination
            paginator = Paginator(projects, per_page)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'projects': page_obj,
                'faculty': faculty,
                'search_query': search_query,
                'paginator': paginator,
                'per_page': per_page,
                'sort_column': sort_column,
                'sort_order': sort_order,
            }
            return render(request, 'mtechMinorEval/projectsList.html', context)

        else:
            logout(request)
            return redirect('login')
    else:
        return redirect('login')


@login_required(login_url='login')
def evaluate(request, pk):
    "Evaluate takes the faculty to the evaluation form of the respective form and can be run by only logged in users.."
    project = Project.objects.get(id=pk)
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    
    if project.guide == faculty:
        FormClass = GuideEvaluationForm
        role = 'Guide'
        initial_data = {'project': project, 'guide': faculty}
        evaluation_instance = GuideEvaluation.objects.filter(project=project, guide=faculty).first()
    elif project.examiner == faculty:
        FormClass = ExaminerEvaluationForm
        role = 'Examiner'
        initial_data = {'project': project, 'examiner': faculty}
        evaluation_instance = ExaminerEvaluation.objects.filter(project=project, examiner=faculty).first()
    else:
        return HttpResponse("You are not authorized to access this resource")

    if request.method == 'POST':
        if evaluation_instance:
            form = FormClass(request.POST, instance=evaluation_instance, initial=initial_data)
        else:
            form = FormClass(request.POST, initial=initial_data)
        
        if form.is_valid():
            form.save()
            faculty.done=False
            faculty.save()
            log_activity.delay(f"{faculty.name} evaluated {project.student.name}'s project ( {project.title} )as a {role}")
            return redirect('projectsList')
        else:
            print("Form is invalid")
    else:
        if evaluation_instance:
            form = FormClass(instance=evaluation_instance, initial=initial_data)
        else:
            form = FormClass(initial=initial_data)

    total_marks = 0
    if evaluation_instance:
        total_marks = (
            getattr(evaluation_instance, 'depthOfUnderstanding', 0) +
            getattr(evaluation_instance, 'workDoneAndResults', 0) +
            getattr(evaluation_instance, 'exceptionalWork', 0) +
            getattr(evaluation_instance, 'vivaVoce', 0) +
            getattr(evaluation_instance, 'presentation', 0) +
            getattr(evaluation_instance, 'report', 0) +
            getattr(evaluation_instance, 'attendance', 0)
        )
    context = {'form': form, 'role': role,'total_marks':total_marks,'project':project,'faculty':faculty}
    return render(request, 'mtechMinorEval/projectEvaluation.html', context=context)



@login_required(login_url='login')
def generate_pdf(request):
    "Generates pdf of the evaluation report and can be run by only logged in users."
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')\
                              .filter(Q(guide=faculty) | Q(examiner=faculty))
    guide_projects_count = Project.objects.filter(guide=faculty).count()
    examiner_projects_count = Project.objects.filter(examiner=faculty).count()

    context = {
        'projects': projects,
        'faculty':faculty,
        'guide_count':guide_projects_count,
        'examiner_count':examiner_projects_count
    }
    
    # Check if the user wants to download the PDF
    if 'download' in request.GET:
        html_string = render_to_string('mtechMinorEval/generate-pdf-summary.html', context)
        pdf_file = HTML(string=html_string).write_pdf()

        # Return the PDF as an HTTP response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="evaluation_summary.pdf"'
        return response
    log_activity.delay(f"{faculty.name} generated report of his evaluation")
    return render(request,'mtechMinorEval/generate-pdf-summary.html', context)



def faculty_specific_eval(request,pk):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'student__rollno')  
    sort_order = request.GET.get('order', 'asc')
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column 

    projects=ProjectEvalSummary.objects.filter(Q(guide=faculty) |
                                                Q(examiner=faculty) )
    
    projects=projects.filter(Q(project__title__icontains=search_query) |
                                                  Q(student__name__icontains=search_query) |
                                                   Q(student__rollno__icontains=search_query) 
    ).order_by(order_by)
    
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
        'faculty':faculty,
        'projects':page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request,'mtechMinorEval/facultySpecific.html',context)


@login_required
def student_profile_view(request,pk):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    student = Student.objects.get(id=pk)
    profile = student.profile 
    form =StudentEditForm(instance=student)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES,instance=student)
        profile_form = ProfileEditForm(request.POST, instance=profile) 
    context = {
        'student': student,
        'form': form,
        'profile_form': profile_form,
        'faculty':faculty  
    }
    log_activity.delay(f"{faculty.name} viewed {student.name}'s profile")
    return render(request,'users/student_profile.html',context)




@login_required(login_url='login')
def send_evaluation_report_to_faculty(request):
    # Get faculty object
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)

    if not faculty.done:
        # Update the 'done' field
        faculty.done = True
        faculty.save()

        # Generate the PDF
        projects = Project.objects.select_related('student', 'guide', 'examiner')\
                                  .prefetch_related('guide_evaluation', 'examiner_evaluation')\
                                  .filter(Q(guide=faculty) | Q(examiner=faculty))
        guide_projects_count = Project.objects.filter(guide=faculty).count()
        examiner_projects_count = Project.objects.filter(examiner=faculty).count()

        context = {
            'projects': projects,
            'faculty': faculty,
            'guide_count': guide_projects_count,
            'examiner_count': examiner_projects_count
        }

        html_string = render_to_string('mtechMinorEval/generate-pdf-summary.html', context)
        pdf_file = HTML(string=html_string).write_pdf()

        # Send email with PDF as an attachment
        subject = 'MTech IT Minor Project Marks Finalized Report'
        message = f'Hello {faculty.name},\n\nYou have successfully finalized the MTech IT Minor Project Marks.'
        email = EmailMessage(subject, message, os.getenv("EMAIL"), [faculty.email])

        # Attach the PDF
        email.attach('evaluation_summary.pdf', pdf_file, 'application/pdf')

        # Use a thread to send the email in the background
        email_thread = threading.Thread(target=email.send)
        email_thread.start()
        log_activity.delay(f"Evaluation report sent to {faculty.name}")

        messages.success(request, 'Evaluation finalized, and email with PDF sent.')

    return redirect('projectsList')  # Redirect to the relevant page