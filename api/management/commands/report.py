from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
import csv


class Command(BaseCommand):
    help = 'Report ocr result'

    def read_csv(self, file_name, sorted_key="Name"):
        with open(file_name, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            return sorted(list(reader), key= lambda k: k[sorted_key])

    def merge_csv_files(self, base_file, base_keys, merge_file, merge_keys ):
        base= self.read_csv(settings.BASE_DIR + base_file)
        merge =  self.read_csv(settings.BASE_DIR + merge_file)
        for i in range(len(base)):
            for index, base_key in enumerate(base_keys):
                base[i][base_key] = merge[i][merge_keys[index]]
        return base

    def handle(self, *args, **options):
        merge_keys = ["predict2", "cer2", "wer2"]
        list_rows = self.merge_csv_files("/static/self_train.csv", merge_keys, "/static/pretrained.csv", merge_keys)
        context = {"list_rows": list_rows, "image_folder": "/home/osboxes/Downloads/viebest_data/skew_deshadow/"}
        rendered = render_to_string('report.html',context)
        with open(settings.BASE_DIR+"/static/report.html","w+") as file:
            file.write(rendered)



