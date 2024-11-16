from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Faculty,Student
from mtechMinorEval.forms import ProfileEditForm, ProjectEditForm, StudentEditForm, FacultyEditForm
from mtechMinorEval.models import Project
from .tasks import log_activity
from django.core.cache import cache

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editProject(request, pk):
    "Edit a particular project details"
    project = get_object_or_404(Project, id=pk) 
    if request.method == 'POST':
        form = ProjectEditForm(request.POST, request.FILES,instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project details updated successfully.')
            log_activity.delay(f"Admin edited {project.student.name}'s project ({project.title}) details")
            cache.clear()
            return redirect('project-allotment') 
        else:
            messages.error(request, form.errors)
    else:
        form = ProjectEditForm(instance=project)
    
    context = {
        'project': project,
        'form': form
    }
    return render(request, 'mtechMinorEval/editProject.html', context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editStudent(request, pk):
    "Edit a paritcular student details"
    student = Student.objects.get(id=pk)
    profile = student.profile 
    form =StudentEditForm(instance=student)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES,instance=student)
        profile_form = ProfileEditForm(request.POST, instance=profile) 

        if form.is_valid() and profile_form.is_valid(): 
            form.save()     
            profile_instance = profile_form.save(commit=False)  
            user = profile.user  
            user.email = profile_instance.email  
            user.save()  
            profile_instance.save()  
            messages.success(request, 'Student updated successfully!')
            log_activity.delay(f"Admin edited {student.name}'s details")
            cache.clear()
            return redirect('student-database')  
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'student': student,
        'form': form,
        'profile_form': profile_form  
    }
    return render(request, 'mtechMinorEval/editStudent.html', context)


@login_required
def editFaculty(request, pk):
    "Edit a particular faculty details"
    if request.user.is_superuser:
        template = "mtechMinorEval/base.html"
    else:
        template = "mtechMinorEval/base_faculty.html"
    faculty = Faculty.objects.get(id=pk)
    profile = faculty.profile 
    form = FacultyEditForm(instance=faculty)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = FacultyEditForm(request.POST,request.FILES, instance=faculty)
        profile_form = ProfileEditForm(request.POST, instance=profile) 

        if form.is_valid() and profile_form.is_valid(): 
            print(form)
            form.save()     
            profile_instance = profile_form.save(commit=False)  
            user = profile.user  
            user.email = profile_instance.email  
            user.save()  
            profile_instance.save()  

            messages.success(request, 'Faculty updated successfully!')
            if request.user.is_superuser:
                log_activity.delay(f"Admin edited {faculty.name}'s details")
                cache.clear()
            else:
                log_activity.delay(f"{faculty.name} updated his details")
                cache.clear()
            if request.user.is_superuser:
                return redirect('faculty-database')  
            else:
                return redirect('projectsList')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'faculty': faculty,
        'form': form,
        'profile_form': profile_form  
    }
    if request.user.is_superuser: 
        return render(request, 'mtechMinorEval/editFaculty.html', context)
    else:
        return render(request,'mtechMinorEval/facultyEdit.html',context)

