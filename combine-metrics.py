import os
import json
import csv


RAW_DIR = "results-raw"
COMBINED_DIR = "results-combined"


def combine_metrics():
    for name in os.listdir(RAW_DIR):
        if os.path.isdir(os.path.join(RAW_DIR, name)):
            print(name)
            with open(os.path.join(RAW_DIR, name, f"{name}-radon.csv"), "r") as radon_file:
                radon_data = radon_file.read()
                radon_metrics_names = radon_data.split("\n")[0].split(",")
                radon_metrcis = radon_data.split("\n")[1].split(",")

            with open(os.path.join(RAW_DIR, name, f"{name}-summary.json"), "r") as sourcemeter_file:
                sourcemeter_data = json.loads(sourcemeter_file.read())
        
        sourcemeter = sourcemeter_data["nodes"][0]["attributes"]
        sourcemeter_metrics = []
        sourcemeter_metrics_names = []

        for metric in sourcemeter:
            if metric["name"] != "Name" and metric["name"] != "LongName":
                sourcemeter_metrics_names.append(metric["name"])
                sourcemeter_metrics.append(metric["value"])


        overall_names = ["Name"] + radon_metrics_names + sourcemeter_metrics_names
        overall_metrics = [name] + radon_metrcis + sourcemeter_metrics

        try:
            os.mkdir(os.path.join(COMBINED_DIR, name))
        except FileExistsError:
            pass

        if not os.path.exists(os.path.join(COMBINED_DIR, name, f"{name}-combined.csv")):
            with open(os.path.join(COMBINED_DIR, name, f"{name}-combined.csv"), "w") as combined_file:
                writer = csv.writer(combined_file, lineterminator="\n")
                writer.writerow(overall_names)
                writer.writerow(overall_metrics)


if __name__ == "__main__":
    try:
        os.mkdir(COMBINED_DIR)
    except FileExistsError:
        pass

    combine_metrics()
