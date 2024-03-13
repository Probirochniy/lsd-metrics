import subprocess
import csv
import os
import shutil
import stat

from radon.metrics import h_visit, mi_visit
from radon.complexity import cc_visit
import csv
import glob

# Constants
CSV_PATH = "repositories.csv"
EXE_PATH = "SourceMeter-10.2.0-x64-Windows\\Python\\AnalyzerPython.exe"
RESULTS_DIR = "results-raw"


# Function to remove the readonly attribute from a file, helps to delete the repository
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def prepare_for_sourcemeter(directory):
    with open(os.path.join(directory, "__init__.py"), "w") as f:
        f.write("")

    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            init_path = os.path.join(root, dir, "__init__.py")
            with open(init_path, "w") as f:
                f.write("")

        for file in files:
            if not file.endswith(".py"):
                try:
                    os.remove(os.path.join(root, file))
                except PermissionError:
                    remove_readonly(os.remove, os.path.join(root, file), None)


# Function to write the resulting radon metrics to a csv file
def write_metrics_to_csv(metrics, csv_path):
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(metrics.keys())
        writer.writerow(metrics.values())


# Function that collects the radon metrics
def get_radon_metrics(name):
    repo_path = os.path.join(name, "**", "*.py")
    files = glob.glob(repo_path, recursive=True)

    # Maintainability index
    total_mi = 0

    # Halstead metrics
    total_h = {
        "h1": 0,
        "h2": 0,
        "N1": 0,
        "N2": 0,
        "vocabulary": 0,
        "length": 0,
        "volume": 0,
        "difficulty": 0,
        "effort": 0,
        "time": 0,
        "bugs": 0,
    }
    total_files = 0

    # Cyclomatic complexity
    total_complexity = 0
    total_functions = 0

    average_complexity = 0

    for file in files:
        # Some files fail for various reasons
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                blocks = cc_visit(content)
                for block in blocks:
                    total_complexity += block.complexity
                    total_functions += 1
                average_complexity += (
                    total_complexity / total_functions if total_functions else 0
                )
            # Error that happens in some repos due to the bug, apparently
            except SyntaxError:
                pass
            mi = mi_visit(content, True)
            total_mi += mi

            h = h_visit(content)
            cur_h_total = getattr(h, "total")
            for key in total_h.keys():
                total_h[key] += getattr(cur_h_total, key)

            total_files += 1

            print(f"Radon processed {total_files} files / {len(files)}", end="\r")
        except:
            pass

    average_mi = total_mi / total_files if total_files else 0
    average_h = {
        key: total_h[key] / total_files if total_files else 0 for key in total_h.keys()
    }
    average_complexity = average_complexity / total_files if total_files else 0

    result = average_h.copy()
    result["MI"] = average_mi
    result["CC"] = average_complexity

    return result


# Function that collects the sourcemeter metrics
def get_source_meter_metrics(name):
    results_dir = f"{name}-results"

    # Running the SourceMeter tool
    args = [
        EXE_PATH,
        f"-projectBaseDir={name}",
        f"-projectName={name}",
        f"-resultsDir={results_dir}",
        "-pythonVersion=3",
        f"-pythonBinary=python3",
    ]
    subprocess.run(args)

    # Moving the summary files to the results directory
    path = f".\{results_dir}\{name}\python"
    summary_name = f"{name}-summary.json"
    dirs = os.listdir(path)

    for dir in dirs:
        try:
            old_path = os.path.join(path, dir, summary_name)
            new_path = os.path.join(RESULTS_DIR, name, summary_name)
            shutil.copyfile(old_path, new_path)
        except FileNotFoundError as e:
            print(e)

    # Deleting the temporary directory
    shutil.rmtree(results_dir, onerror=remove_readonly)


# Function that collects all metrics
def get_metrics(names_links):
    for name, link in names_links:
        print(name, link)

        # Creating the directory for the repository
        repo_results_dir = os.path.join(RESULTS_DIR, name)

        try:
            os.mkdir(repo_results_dir)
        except FileExistsError:
            pass
        
        # Cloning the repository
        subprocess.run(["git", "clone", "--depth", "1", link, name])

        # Creating the __init__.py files
        # Getting the sourcemeter metrics
        prepare_for_sourcemeter(name)
        try:
            get_source_meter_metrics(name)
        except:
            pass

        # Getting the radon metrics
        temp_name = os.path.join(RESULTS_DIR, name, f"{name}-radon.csv")
        result = get_radon_metrics(name)
        write_metrics_to_csv(result, temp_name)

        # Deleting the repository
        shutil.rmtree(name, onerror=remove_readonly)


def main():

    try:
        os.mkdir(RESULTS_DIR)
    except FileExistsError:
        pass

    names_links = []

    # Getting the names and links from the csv file
    with open(CSV_PATH, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            names_links.append((row[0], row[1]))
        names_links = names_links[1:]

    #Temp
    names_links = names_links[6:]

    get_metrics(names_links)


if __name__ == "__main__":
    main()
