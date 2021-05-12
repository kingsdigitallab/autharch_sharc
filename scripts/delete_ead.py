from ead.models import EAD


def run():
    EAD.objects.all().delete()
