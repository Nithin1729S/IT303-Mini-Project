from django.core.management.base import BaseCommand
from mtechMinorEval.models import Project, ProjectEvalSummary, GuideEvaluation, ExaminerEvaluation

class Command(BaseCommand):
    help = 'Updates all ProjectEvalSummary instances'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        for project in projects:
            eval_summary, created = ProjectEvalSummary.objects.get_or_create(project=project)
            
            # Update basic info
            eval_summary.student = project.student
            eval_summary.guide = project.guide
            eval_summary.examiner = project.examiner

            # Update guide score
            guide_eval = GuideEvaluation.objects.filter(project=project).first()
            if guide_eval:
                eval_summary.guide_score = guide_eval.total_score

            # Update examiner score
            examiner_eval = ExaminerEvaluation.objects.filter(project=project).first()
            if examiner_eval:
                eval_summary.examiner_score = examiner_eval.total_score

            eval_summary.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated all ProjectEvalSummary instances'))