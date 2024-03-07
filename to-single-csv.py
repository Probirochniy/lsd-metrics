import csv
import os


COMBINED_DIR = "results-combined"
CSV_PATH = "metrics.csv"


def combine_to_single_csv():
    with open(CSV_PATH, "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        first_name = os.listdir(COMBINED_DIR)[0]
        with open(
            os.path.join(COMBINED_DIR, first_name, f"{first_name}-combined.csv"), "r"
        ) as combined_file:
            reader = csv.reader(combined_file)
            writer.writerow(next(reader))

        for name in os.listdir(COMBINED_DIR):
            if os.path.isdir(os.path.join(COMBINED_DIR, name)):
                with open(
                    os.path.join(COMBINED_DIR, name, f"{name}-combined.csv"), "r"
                ) as combined_file:
                    reader = csv.reader(combined_file)
                    next(reader)
                    writer.writerow(next(reader))


if __name__ == "__main__":
    combine_to_single_csv()
