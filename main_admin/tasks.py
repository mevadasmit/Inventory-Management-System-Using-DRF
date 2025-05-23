import csv , os
from datetime import timedelta
from django.utils.timezone import now
from celery import shared_task
from .models import Organization

EXPORT_DIR  = '/home/root491/csv_logs/csv_exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

@shared_task
def export_org_csv():
    end_time = now()
    start_time = end_time - timedelta(minutes=5)

    qs = Organization.objects.filter(
        updated__gte=start_time,
        updated__lt=end_time
    )

    filename = f"org_{start_time.strftime('%Y%m%d_%H%M')}_to_{end_time.strftime('%H%M')}.csv"
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID','Name','Email','Address','Created_at','Updated_at'])
        for org in qs:
            writer.writerow([str(org.id),
                             org.name, org.email, org.address,
                             org.created.isoformat(), org.updated.isoformat()])
    print(f"[export_org_csv] Wrote {qs.count()} org(s) to {path}")
    return f"Wrote {qs.count()} organizations to {path}"