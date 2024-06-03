import os
import subprocess
import sys
import shutil


def ensure_clamav_in_path():
    """
    Ensures that ClamAV executables are in the system PATH.
    If not, adds the default installation path to PATH.
    """
    clamav_path = "C:\\Program Files\\ClamAV"

    # Check if ClamAV is in the PATH
    if not any(clamav_path in p for p in os.environ["PATH"].split(os.pathsep)):
        print(f"ClamAV not found in PATH. Adding {clamav_path} to PATH.")

        # Add ClamAV to PATH
        os.environ["PATH"] += os.pathsep + clamav_path

        # Permanently add ClamAV to PATH for the current user
        subprocess.run(['setx', 'PATH', os.environ["PATH"]], shell=True)
        print("ClamAV added to PATH.")
    else:
        print("ClamAV is already in PATH.")


def get_clamav_paths():
    """
    Get the paths for ClamAV database and log directory.
    If not found, prompt the user to provide them.
    """
    db_path = os.environ.get('CLAMAV_DB_PATH') or "C:\\Program Files\\ClamAV\\db"
    log_dir = os.environ.get('CLAMAV_LOG_DIR') or "C:\\Users\\Public\\clamav_logs"

    if not os.path.isdir(db_path):
        db_path = input(f"ClamAV database path not found at {db_path}. Please provide the correct path: ")

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    return db_path, log_dir


def update_clamav_db(log_file):
    """
    Updates the ClamAV database.
    """
    try:
        result = subprocess.run(['freshclam', '--log', log_file], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)


def scan_directory(directory, db_path):
    """
    Scans the specified directory with ClamAV.
    """
    try:
        scanned_items = 0
        process = subprocess.Popen(['clamscan', '-r', '--database', db_path, directory], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)

        full_output = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                scanned_items += 1
                sys.stdout.write(f"\rItems scanned: {scanned_items}")
                sys.stdout.flush()
                full_output.append(output.strip())

        final_output, _ = process.communicate()
        full_output.append(final_output.strip())
        print()
        return '\n'.join(full_output)
    except Exception as e:
        return str(e)


def quick_scan(db_path):
    """
    Performs a quick scan on critical directories with ClamAV.
    """
    critical_dirs = ['C:\\Windows', 'C:\\Program Files', 'C:\\Users']
    try:
        scanned_items = 0
        process = subprocess.Popen(['clamscan', '-r', '--database', db_path] + critical_dirs, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)

        full_output = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                scanned_items += 1
                sys.stdout.write(f"\rItems scanned: {scanned_items}")
                sys.stdout.flush()
                full_output.append(output.strip())

        final_output, _ = process.communicate()
        full_output.append(final_output.strip())
        print()
        return '\n'.join(full_output)
    except Exception as e:
        return str(e)


def scan_entire_computer(db_path):
    """
    Scans the entire computer with ClamAV.
    """
    try:
        scanned_items = 0
        process = subprocess.Popen(['clamscan', '-r', '--database', db_path, 'C:\\'], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)

        full_output = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                scanned_items += 1
                sys.stdout.write(f"\rItems scanned: {scanned_items}")
                sys.stdout.flush()
                full_output.append(output.strip())

        final_output, _ = process.communicate()
        full_output.append(final_output.strip())
        print()
        return '\n'.join(full_output)
    except Exception as e:
        return str(e)


def main():
    ensure_clamav_in_path()
    db_path, log_dir = get_clamav_paths()
    log_file = os.path.join(log_dir, "freshclam.log")

    while True:
        print("\nChoose an option for ClamAV scan:")
        print("1. Scan a specific directory")
        print("2. Quick scan (critical directories)")
        print("3. Full scan (entire computer)")
        print("4. Exit")
        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '4':
            print("Exiting...")
            break

        print("Updating ClamAV database...")
        update_result = update_clamav_db(log_file)
        print("ClamAV Database Update Result:")
        print(update_result)

        if "ERROR" in update_result:
            print("Error updating ClamAV database.")
        else:
            if choice == '1':
                directory = input("Enter the directory to scan: ")
                if os.path.isdir(directory):
                    print("Scanning directory:", directory)
                    result = scan_directory(directory, db_path)
                    print("\nClamAV Scan Result:")
                    print(result)
                else:
                    print(f"The directory {directory} does not exist.")
            elif choice == '2':
                print("Performing quick scan on critical directories...")
                result = quick_scan(db_path)
                print("\nClamAV Scan Result:")
                print(result)
            elif choice == '3':
                print("Performing full scan (entire computer)...")
                result = scan_entire_computer(db_path)
                print("\nClamAV Scan Result:")
                print(result)
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
