import subprocess
import sys
import time
import msvcrt
import os
import ctypes
import shutil
import argparse
from datetime import datetime
import fnmatch

def set_cmd_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def print_wap_banner():
    banner ="""---------------------------------------
 _      __  ___     ___
| | /| / / / _ |   / _ \\
| |/ |/ / / __ |  / ___/
|__/|__/ /_/ |_| /_/

Windows Artifact Parser
---------------------------------------"""
    print(banner)

def check_admin_rights():
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except AttributeError:
            is_admin = False
    else:
        is_admin = True

    if not is_admin:
        sys.exit("[ERROR] This tool requires administrative privileges to run.")

def find_files_path(directory, filename):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        if filename in files:
            file_paths.append(os.path.join(root, filename))

    return file_paths

def check_file_and_get_path(directory, target_file):
    for root, dirs, files in os.walk(directory):
        if target_file in files:
            path = os.path.join(root, target_file)
            return path
    return None

def check_file_extension(directory, extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                return True
    return False

def test_zip(zip_file_path):
    try:
        cmd_command = ['lib\\7-Zip\\7z.exe', 't', '-p1234', zip_file_path, "-y"]

        process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("[INFO] ZIP Verified Successfully")
            return True
        else:
            return False

    except Exception as e:
        print(f"[ERROR] Exception occurred during extraction: {e}")
        sys.exit(1)
        return False

def unzip_directory(zip_file_path, password=None):
    try:
        file_name = zip_file_path.split("\\")[-1]
        cmd_command = ['lib\\7-Zip\\7z.exe', 'x', f'-oWAP_Extraction_{file_name}\\Extracted_Data', zip_file_path, "-y"]
        if password:
            cmd_command.insert(2, f'-p{password}')

        print("[INFO] Started Unzipping Module")

        process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("[INFO] Extraction successful\n")
            return True
        else:
            print(f"[ERROR] Extraction failed. Error: {stderr.strip()}\n")
            return False

    except Exception as e:
        print(f"[ERROR] Exception occurred during extraction: {e}\n")
        return False

def amcache(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    amcache_path = check_file_and_get_path(base_directory, "Amcache.hve")

    if amcache_path:
        print("[+] Amcache.hve found\n")
        print("[INFO] Started Amcache Parser Module")

        if zip:
            cmd_command = ['lib\\AmcacheParser.exe', '-f', f'{amcache_path}', '--csv', f'WAP_Extraction_{file_name}\\Results\\Amcache\\']
        else:
            cmd_command = ['lib\\AmcacheParser.exe', '-f', f'{amcache_path}', '--csv', f'Results_{file_name}\\Amcache\\']

        try:
            process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                if zip:
                    cmd_command = ['lib\\RegRipper\\rip.exe', '-r', f'{amcache_path}', '-a', '>', f'WAP_Extraction_{file_name}\\Results\\Amcache\\Amcache_RegRipper.txt']
                else:
                    cmd_command = ['lib\\RegRipper\\rip.exe', '-r', f'{amcache_path}', '-a', '>', f'Results_{file_name}\\Amcache\\Amcache_RegRipper.txt']
                try:
                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    if process.returncode == 0:
                        print("[INFO] Amcache Parsed Successfully\n")
                    else:
                        print(f"[ERROR] Amcache Parsing Failed. Error: {process.stderr.strip()}\n")
                except Exception as e:
                    print(f"[ERROR] Exception occurred during amcache parsing using RegRipper. Error: {e}\n")
            else:
                print(f"[ERROR] Amcache Parsing Failed. Error: {stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during amcache parsing using AmcacheParser. Error: {e}\n")
    else:
        print("[-] Amcache.hve not found\n")

def browser_data(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    chrome_paths = []
    edge_paths = []
    firefox_paths = []
    results = find_files_path(base_directory, "History")
    if results != None:
        for path in results:
            if "Snapshots" not in path:
                if "Chrome" in path:
                    chrome_paths.append(path)
                if "Edge" in path:
                    edge_paths.append(path)

    print("[+] Chrome Data found" if chrome_paths else "[-] Chrome Data not found")
    print("[+] Edge Data found" if edge_paths else "[-] Edge Data not found")

    results = find_files_path(base_directory, "places.sqlite")
    if results != None:
        for path in results:
            firefox_paths.append(path)

    print("[+] Firefox Data found" if firefox_paths else "[-] Firefox Data not found")

    if chrome_paths or edge_paths or firefox_paths:
        if zip:
            os.mkdir(f"WAP_Extraction_{file_name}\\Results\\Browser_Data")
        else:
            os.mkdir(f"Results_{file_name}\\Browser_Data")

        try:
            if chrome_paths:
                print("\n[INFO] Started Chrome Data Parser Module")
                for final_path in chrome_paths:
                    username = final_path.split("\\")[-8]
                    final_path.replace("\\","/")

                    if zip:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output WAP_Extraction_{file_name}/Results/Browser_Data/chrome_history_{username}.csv', 'SELECT * FROM URLS;' ]
                    else:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output Results_{file_name}/Browser_Data/chrome_history_{username}.csv', 'SELECT * FROM URLS;' ]

                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    time.sleep(1)

                    if zip:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output WAP_Extraction_{file_name}/Results/Browser_Data/chrome_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,BY_WEB_APP_ID,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;']
                    else:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output Results_{file_name}/Browser_Data/chrome_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,BY_WEB_APP_ID,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;']

                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    time.sleep(1)

                print("[INFO] Chrome Data Parsed Successfully")

            if edge_paths:
                print("\n[INFO] Started Edge Data Parser Module")
                for final_path in edge_paths:
                    username = final_path.split("\\")[-8]

                    if zip:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output WAP_Extraction_{file_name}/Results/Browser_Data/edge_history_{username}.csv', 'SELECT * FROM URLS;' ]
                    else:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output Results_{file_name}/Browser_Data/edge_history_{username}.csv', 'SELECT * FROM URLS;' ]

                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    time.sleep(1)

                    if zip:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output WAP_Extraction_{file_name}/Results/Browser_Data/edge_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;' ]
                    else:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output Results_{file_name}/Browser_Data/edge_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;' ]

                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    time.sleep(1)

                print("[INFO] Edge Data Parsed Successfully")

            if firefox_paths:
                print("\n[INFO] Started Firefox Data Parser Module")
                for final_path in firefox_paths:
                    username = final_path.split("\\")[-8]

                    if zip:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output WAP_Extraction_{file_name}/Results/Browser_Data/firefox_history_{username}.csv', 'SELECT * FROM MOZ_PLACES;' ]
                    else:
                        cmd_command = ['lib\\sqlite\\sqlite3.exe', final_path, '.headers on', '.mode csv', f'.output Results_{file_name}/Browser_Data/firefox_history_{username}.csv', 'SELECT * FROM MOZ_PLACES;' ]

                    process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                    time.sleep(1)

                print("[INFO] Firefox Data Parsed Successfully")
            print("")
        except Exception as e:
            print(f"[ERROR] Browser Data Parsing Failed. Error: {e}\n")
    else:
        print("")

def jumplist(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    jumplist_custom = check_file_extension(base_directory, ".customDestinations-ms")
    jumplist_automatic = check_file_extension(base_directory, ".automaticDestinations-ms")

    if jumplist_custom or jumplist_automatic:
        print("[+] Jumplist found\n")
        print("[INFO] Started Jumplist Parser Module")

        if zip:
            cmd_command = ['lib\\JLECmd.exe', '-q', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Jumplist', '>', 'NUL']
        else:
            cmd_command = ['lib\\JLECmd.exe', '-q', '-d', base_directory, '--csv', f'Results_{file_name}\\Jumplist', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print("[INFO] Jumplist Parsed Successfully\n")
            else:
                print(f"[ERROR] Jumplist Parsing Failed. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during jumplist parsing. Error: {e}\n")
    else:
        print("[-] Jumplist not found\n")

def mft(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    mft_path = check_file_and_get_path(base_directory, "$MFT")

    if mft_path:
        print("[+] $MFT found\n")
        print("[INFO] Started $MFT Parser Module")

        if zip:
            cmd_command = ['lib\\MFTECmd.exe', '-f', mft_path, '--csv', f'WAP_Extraction_{file_name}\\Results\\MFT']
        else:
            cmd_command = ['lib\\MFTECmd.exe', '-f', mft_path, '--csv', f'Results_{file_name}\\MFT']
        try:
            process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print("[INFO] $MFT Parsed Successfully\n")
            else:
                print(f"[ERROR] $MFT Parsing Failed. Error: {stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during $MFT parsing. Error: {e}\n")
    else:
        print("[-] $MFT not found\n")

def usnlog(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    usn_path = check_file_and_get_path(base_directory, "$J")
    log_path = check_file_and_get_path(base_directory, "$LogFile")

    print("[+] $J (UsnJournal) found" if usn_path else "[-] $J (UsnJournal) not found")
    print("[+] $LogFile found" if log_path else "[-] $LogFile not found")

    if usn_path or log_path:
        if usn_path and log_path:
            print("\n[INFO] Started UsnJournal and $LogFile Parser Module")
            final_msg = "[INFO] UsnJournal and $LogFile Parsed Successfully\n"
            error_msg = "[ERROR] UsnJournal and $LogFile Parsing Failed."
            exception_msg = "[ERROR] Exception occurred during UsnJournal and $LogFile parsing."
            if zip:
                os.mkdir(f"WAP_Extraction_{file_name}\\Results\\UsnJournalandLogFile")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-u', usn_path, '-m', mft_path, '-o', f'WAP_Extraction_{file_name}\\Results\\UsnJournalandLogFile', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-u', usn_path, '-o', f'WAP_Extraction_{file_name}\\Results\\UsnJournalandLogFile', '-b', '-c', '>', 'NUL']
            else:
                os.mkdir(f"Results_{file_name}\\UsnJournalandLogFile")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-u', usn_path, '-m', mft_path, '-o', f'Results_{file_name}\\UsnJournalandLogFile', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-u', usn_path, '-o', f'Results_{file_name}\\UsnJournalandLogFile', '-b', '-c', '>', 'NUL']
        if usn_path and not log_path:
            print("\n[INFO] Started UsnJournal Parser Module")
            final_msg = "[INFO] UsnJournal Parsed Successfully\n"
            error_msg = "[ERROR] UsnJournal Parsing Failed."
            exception_msg = "[ERROR] Exception occurred during UsnJournal parsing."
            if zip:
                os.mkdir(f"WAP_Extraction_{file_name}\\Results\\UsnJournal")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-u', usn_path, '-m', mft_path, '-o', f'WAP_Extraction_{file_name}\\Results\\UsnJournal', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-u', usn_path, '-o', f'WAP_Extraction_{file_name}\\Results\\UsnJournal', '-b', '-c', '>', 'NUL']
            else:
                os.mkdir(f"Results_{file_name}\\UsnJournal")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-u', usn_path, '-m', mft_path, '-o', f'Results_{file_name}\\UsnJournal', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-u', usn_path, '-o', f'Results_{file_name}\\UsnJournal', '-b', '-c', '>', 'NUL']
        if not usn_path and log_path:
            print("\n[INFO] Started $LogFile Parser Module")
            final_msg = "[INFO] $LogFile Parsed Successfully\n"
            error_msg = "[ERROR] $LogFile Parsing Failed."
            exception_msg = "[ERROR] Exception occurred during $LogFile parsing."
            if zip:
                os.mkdir(f"WAP_Extraction_{file_name}\\Results\\LogFile")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-m', mft_path, '-o', f'WAP_Extraction_{file_name}\\Results\\LogFile', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-o', f'WAP_Extraction_{file_name}\\Results\\LogFile', '-b', '-c', '>', 'NUL']
            else:
                os.mkdir(f"Results_{file_name}\\LogFile")
                mft_path = check_file_and_get_path(base_directory, "$MFT")
                if mft_path:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-m', mft_path, '-o', f'Results_{file_name}\\LogFile', '-b', '-c', '>', 'NUL']
                else:
                    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', log_path, '-o', f'Results_{file_name}\\LogFile', '-b', '-c', '>', 'NUL']
        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print(final_msg)
            else:
                print(f"{error_msg} Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"{exception_msg} Error: {e}\n")
    else:
        print("")

def prefetch(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    prefetch_present = check_file_extension(base_directory, ".pf")

    if prefetch_present:
        print("[+] Prefetch found\n")
        print("[INFO] Started Prefetch Parser Module")

        if zip:
            cmd_command = ['lib\\PECmd.exe', '-q', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Prefetch_Files', '>', 'NUL']
        else:
            cmd_command = ['lib\\PECmd.exe', '-q', '-d', base_directory, '--csv', f'Results_{file_name}\\Prefetch_Files', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print("[INFO] Prefetch Parsed Successfully\n")
            else:
                print(f"[ERROR] Prefetch Parsing Failed. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during prefetch parsing. Error: {e}\n")
    else:
        print("[-] Prefetch not found\n")

def recent_files(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    recent_files_present = check_file_extension(base_directory, ".lnk")

    if recent_files_present:
        print("[+] Recent Files found\n")
        print("[INFO] Started Recent Files Parser Module")

        if zip:
            cmd_command = ['lib\\LECmd.exe', '-q', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Recent_Files', '>', 'NUL']
        else:
            cmd_command = ['lib\\LECmd.exe', '-q', '-d', base_directory, '--csv', f'Results_{file_name}\\Recent_Files', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print("[INFO] Recent Files Parsed Successfully\n")
            else:
                print(f"[ERROR] Recent Files Parsing Failed. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during recent files parsing. Error: {e}\n")
    else:
        print("[-] Recent Files not found\n")

def recycle_bin(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    recycle_bin_present = False

    for dirpath, _, filenames in os.walk(base_directory):
        for filename in filenames:
            if fnmatch.fnmatch(filename, '$I*'):
                recycle_bin_present = True
                break

    if recycle_bin_present:
        print("[+] Recycle Bin Files found\n")
        print("[INFO] Started Recycle Bin Parser Module")

        if zip:
            cmd_command = ['lib\\RBCmd.exe', '-q', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Recycle_Bin', '>', 'NUL']
        else:
            cmd_command = ['lib\\RBCmd.exe', '-q', '-d', base_directory, '--csv', f'Results_{file_name}\\Recycle_Bin', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print("[INFO] Recycle Bin Parsed Successfully\n")
            else:
                print(f"[ERROR] Recycle Bin Parsing Failed. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during recycle bin parsing. Error: {e}\n")
    else:
        print("[-] Recycle Bin Files not found\n")

def shellbags(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    ntuser_present = check_file_and_get_path(base_directory, "NTUSER.DAT")
    usrdat_present = check_file_and_get_path(base_directory, "UsrClass.dat")

    print("[+] NTUSER.DAT found" if ntuser_present else "[-] NTUSER.DAT not found")
    print("[+] UsrClass.dat found" if usrdat_present else "[-] UsrClass.dat not found")

    if ntuser_present or usrdat_present:
        print("\n[INFO] Started Shellbags Parser Module")
        if zip:
            cmd_command = ['lib\\SBECmd.exe', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Shellbags', '>', 'NUL']
        else:
            cmd_command = ['lib\\SBECmd.exe', '-d', base_directory, '--csv', f'Results_{file_name}\\Shellbags', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print("[INFO] Shellbags Parsed Successfully\n")
            else:
                print(f"[ERROR] Shellbags Parsing Failed. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during shellbags parsing. Error: {e}\n")
    else:
        print("")

def registry(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    software_hive_present = check_file_and_get_path(base_directory, "SOFTWARE")
    system_hive_present = check_file_and_get_path(base_directory, "SYSTEM")
    sam_hive_present = check_file_and_get_path(base_directory, "SAM")
    security_hive_present = check_file_and_get_path(base_directory, "SECURITY")

    print("[+] SOFTWARE Hive found" if software_hive_present else "[-] SOFTWARE Hive not found")
    print("[+] SYSTEM Hive found" if system_hive_present else "[-] SYSTEM Hive not found")
    print("[+] SAM Hive found" if sam_hive_present else "[-] SAM Hive not found")
    print("[+] SECURITY Hive found" if security_hive_present else "[-] SECURITY Hive not found")

    if software_hive_present or system_hive_present or sam_hive_present or security_hive_present:
        print("\n[INFO] Started Registry Hives Parser Module")

        if zip:
            output_path = f"WAP_Extraction_{file_name}\\Results\\Registry_Hives"
            os.mkdir(output_path)
        else:
            output_path = f"Results_{file_name}\\Registry_Hives"
            os.mkdir(output_path)

        cmd_commands = []

        if software_hive_present:
            cmd_commands.append(['lib\\RegRipper\\rip.exe', '-r', software_hive_present, '-a', '>', f'{output_path}\\SOFTWARE.txt'])
        if sam_hive_present:
            cmd_commands.append(['lib\\RegRipper\\rip.exe', '-r', sam_hive_present, '-a', '>', f'{output_path}\\SAM.txt'])
        if system_hive_present:
            cmd_commands.append(['lib\\RegRipper\\rip.exe', '-r', system_hive_present, '-a', '>', f'{output_path}\\SYSTEM.txt'])
        if security_hive_present:
            cmd_commands.append(['lib\\RegRipper\\rip.exe', '-r', security_hive_present, '-a', '>', f'{output_path}\\SECURITY.txt'])

        try:
            for cmd_command in cmd_commands:
                process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            print("[INFO] Registry Hives Parsed Successfully\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during registry hives parsing. Error: {e}\n")
    else:
        print("")

def event_logs(path, zip=False):
    if zip:
        file_name = path.split("\\")[-1]
        base_directory = f"WAP_Extraction_{file_name}\\Extracted_Data"
    else:
        file_name = path.split("\\")[-1]
        base_directory = path

    event_logs_present = check_file_extension(base_directory, ".evtx")

    if event_logs_present:
        print("[+] Windows Event Logs found\n")
        print("[INFO] Started Windows Event Logs Parser Module")

        if zip:
            os.mkdir(f"WAP_Extraction_{file_name}\\Results\\Windows_Event_Logs")
        else:
            os.mkdir(f"Results_{file_name}\\Windows_Event_Logs")

        cmd_command = ['lib\\APT-Hunter\\APT-Hunter.exe', '-p', base_directory, '-o', 'APT-Hunter', '-allreport', '>', 'NUL']

        try:
            process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                if zip:
                    shutil.move('APT-Hunter', f'WAP_Extraction_{file_name}\\Results\\Windows_Event_Logs')
                    cmd_command = ['lib\\EvtxeCmd\\EvtxECmd.exe', '-d', base_directory, '--csv', f'WAP_Extraction_{file_name}\\Results\\Windows_Event_Logs', '>', 'NUL']
                else:
                    shutil.move('APT-Hunter', f'Results_{file_name}\\Windows_Event_Logs')
                    cmd_command = ['lib\\EvtxeCmd\\EvtxECmd.exe', '-d', base_directory, '--csv', f'Results_{file_name}\\Windows_Event_Logs', '>', 'NUL']

                process = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
                if process.returncode == 0:
                    print("[INFO] Windows Event Logs Parsed Successfully\n")
                else:
                    print(f"[ERROR] Windows Event Logs Parsing Failed Using EvtxeCmd. Error: {process.stderr.strip()}\n")
            else:
                print(f"[ERROR] Windows Event Logs Parsing Failed Using APT-Hunter. Error: {process.stderr.strip()}\n")
        except Exception as e:
            print(f"[ERROR] Exception occurred during windows event logs parsing. Error: {e}\n")
    else:
        print("[-] Windows Event Logs not found\n")

if __name__ == "__main__":
    set_cmd_title("WAP - Windows Artifact Parser")
    check_admin_rights()
    print_wap_banner()
    start_time = time.time()

    zip_file_path, directory, zip_password = None, None, None

    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', help="Path to the artifact zip")
    parser.add_argument('--directory', help="Path to the artifacts directory")
    parser.add_argument('--password', help="Password for the zip file, if it's password-protected")

    args = parser.parse_args()

    if args.directory and args.zip:
        sys.exit("[ERROR] Either --zip or --directory must be provided not both.")
    if args.directory or args.zip:
        if args.zip and not args.password:
            zip_file_path = args.zip
            print("[INFO] Verifying ZIP")
            no_pass_protected = test_zip(zip_file_path)
            if not no_pass_protected:
                sys.exit("[INFO] ZIP is password protected. Run the script with --password [PASSWORD] along with --zip.")
            print("---------------------------------------")
        if args.zip and args.password:
            zip_file_path = args.zip
            zip_password = args.password
        if args.directory:
            directory = args.directory
    else:
        sys.exit("[ERROR] Either --zip or --directory must be provided.")


    if zip_file_path:
        print("Processing:", zip_file_path)
        print("Started at:", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("---------------------------------------")

        unzip_successful = unzip_directory(zip_file_path, zip_password)
        time.sleep(1)

        if unzip_successful:
            zip_file_name = zip_file_path.split("\\")[-1]
            os.mkdir(f"WAP_Extraction_{zip_file_name}\\Results")

            amcache(zip_file_path, True)
            time.sleep(1)

            browser_data(zip_file_path, True)
            time.sleep(1)

            jumplist(zip_file_path, True)
            time.sleep(1)

            mft(zip_file_path, True)
            time.sleep(1)

            usnlog(zip_file_path, True)
            time.sleep(1)

            prefetch(zip_file_path, True)
            time.sleep(1)

            recent_files(zip_file_path, True)
            time.sleep(1)

            recycle_bin(zip_file_path, True)
            time.sleep(1)

            shellbags(zip_file_path, True)
            time.sleep(1)

            registry(zip_file_path, True)
            time.sleep(1)

            event_logs(zip_file_path, True)
            time.sleep(1)
    else:
        print("Processing:", directory)
        print("Started at:", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("---------------------------------------")

        directory_name = directory.split("\\")[-1]
        os.mkdir(f"Results_{directory_name}")

        amcache(directory)
        time.sleep(1)

        browser_data(directory)
        time.sleep(1)

        jumplist(directory)
        time.sleep(1)

        mft(directory)
        time.sleep(1)

        usnlog(directory)
        time.sleep(1)

        prefetch(directory)
        time.sleep(1)

        recent_files(directory)
        time.sleep(1)

        recycle_bin(directory)
        time.sleep(1)

        shellbags(directory)
        time.sleep(1)

        registry(directory)
        time.sleep(1)

        event_logs(directory)
        time.sleep(1)

    end_time = time.time()

    elapsed_time_seconds = end_time - start_time
    hours, remainder = divmod(elapsed_time_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    print("---------------------------------------")
    print(f"Program execution time: {formatted_time}")
    print("---------------------------------------")
