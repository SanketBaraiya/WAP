import subprocess
import sys
import time
import msvcrt
import os
import ctypes
import shutil
import argparse
from datetime import datetime

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
        print("[ERROR] This tool requires administrative privileges to run.")
        print("[INFO] Please run the tool as an administrator.")
        print("Press any key to exit...")
        msvcrt.getch()
        sys.exit(1)

def find_files(directory, filename):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        if filename in files:
            file_paths.append(os.path.join(root, filename))

    return file_paths

def unzip_directory(zip_file_path, password=None):
    if password:
        cmd_command = ['lib\\7-Zip\\7z.exe', 'x', f'-p{password}', '-oWAP_Extraction\\', zip_file_path]
    else:
        cmd_command = ['lib\\7-Zip\\7z.exe', 'x', '-oWAP_Extraction\\', zip_file_path]

    try:
        process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.wait()
        if process.returncode == 0:
            return
        else:
            print("\r[ERROR] Error in extracting zip.")
    except Exception as e:
        print(f"\r[ERROR] Error in extracting zip: {e}")

def amcache():
    global no_error_amcache

    base_directory = f"ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Amcache"
    target_file = "Amcache.hve"
    amcache_path = None

    for root, dirs, files in os.walk(base_directory):
        if target_file in files:
            amcache_path = os.path.join(root, target_file)
            break

    cmd_command = ['lib\\AmcacheParser.exe', '-f', f'{amcache_path}', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Amcache\\']
    amcache_anim_thread = threading.Thread(target=amcache_anim)
    amcache_anim_thread.start()

    try:
        process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.wait()
        if process.returncode == 0:
            cmd_command = ['lib\\RegRipper\\rip.exe', '-r', f'{amcache_path}', '-a', '>', f'ESTK_Extraction_{collected_system_name}\\Results\\Amcache\\Amcache_RegRipper.txt']
            try:
                process = subprocess.run(cmd_command, shell=True)
                if process.returncode == 0:
                    amcache_anim_stop_event.set()
                    amcache_anim_thread.join()
                else:
                    no_error_amcache = False
                    amcache_anim_stop_event.set()
                    amcache_anim_thread.join()
            except Exception as e:
                no_error_amcache = False
                amcache_anim_stop_event.set()
                amcache_anim_thread.join()
        else:
            no_error_amcache = False
            amcache_anim_stop_event.set()
            amcache_anim_thread.join()
    except Exception as e:
        no_error_amcache = False
        amcache_anim_stop_event.set()
        amcache_anim_thread.join()

def browser_data():
    global no_error_browser_data
    os.makedirs(f"ESTK_Extraction_{collected_system_name}\\Results\\Browser_Data")
    browser_data_anim_thread = threading.Thread(target=browser_data_anim)
    browser_data_anim_thread.start()

    chrome_paths = []
    edge_paths = []
    firefox_paths = []
    results = find_files(f"ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Browser_History", "History")
    if results != None:
        for path in results:
            if "Snapshots" not in path:
                if "Chrome" in path:
                    chrome_paths.append(path)
                if "Edge" in path:
                    edge_paths.append(path)

    results = find_files(f"ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Browser_History", "places.sqlite")
    if results != None:
        for path in results:
            firefox_paths.append(path)
    try:
        if chrome_paths != None:
            for path in chrome_paths:
                username = path.split("\\")[-8]
                path.replace("\\","/")
                cmd_command = ['lib\\sqlite\\sqlite3.exe', path, '.headers on', '.mode csv', f'.output ESTK_Extraction_{collected_system_name}/Results/Browser_Data/chrome_history_{username}.csv', 'SELECT * FROM URLS;' ]
                process = subprocess.run(cmd_command, shell=True)
                time.sleep(1)
                if process.returncode == 0:
                    cmd_command = ['lib\\sqlite\\sqlite3.exe', path, '.headers on', '.mode csv', f'.output ESTK_Extraction_{collected_system_name}/Results/Browser_Data/chrome_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,BY_WEB_APP_ID,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;' ]
                    process = subprocess.run(cmd_command, shell=True)
                    time.sleep(1)
                    if process.returncode == 0:
                        pass
                    else:
                        no_error_browser_data = False
                        browser_data_anim_stop_event.set()
                        browser_data_anim_thread.join()
                else:
                    no_error_browser_data = False
                    browser_data_anim_stop_event.set()
                    browser_data_anim_thread.join()

        if edge_paths != None and no_error_browser_data:
            for path in edge_paths:
                username = path.split("\\")[-8]
                cmd_command = ['lib\\sqlite\\sqlite3.exe', path, '.headers on', '.mode csv', f'.output ESTK_Extraction_{collected_system_name}/Results/Browser_Data/edge_history_{username}.csv', 'SELECT * FROM URLS;' ]
                process = subprocess.run(cmd_command, shell=True)
                time.sleep(1)
                if process.returncode == 0:
                    cmd_command = ['lib\\sqlite\\sqlite3.exe', path, '.headers on', '.mode csv', f'.output ESTK_Extraction_{collected_system_name}/Results/Browser_Data/edge_downloads_{username}.csv', 'SELECT ID,GUID,CURRENT_PATH,TARGET_PATH,START_TIME,RECEIVED_BYTES,TOTAL_BYTES,STATE,DANGER_TYPE,INTERRUPT_REASON,HASH,END_TIME,OPENED,LAST_ACCESS_TIME,TRANSIENT,REFERRER,SITE_URL,TAB_URL,TAB_REFERRER_URL,HTTP_METHOD,BY_EXT_ID,BY_EXT_NAME,LAST_MODIFIED,MIME_TYPE,ORIGINAL_MIME_TYPE FROM DOWNLOADS;' ]
                    process = subprocess.run(cmd_command, shell=True)
                    time.sleep(1)
                    if process.returncode == 0:
                        pass
                    else:
                        no_error_browser_data = False
                        browser_data_anim_stop_event.set()
                        browser_data_anim_thread.join()
                else:
                    no_error_browser_data = False
                    browser_data_anim_stop_event.set()
                    browser_data_anim_thread.join()

        if firefox_paths != None and no_error_browser_data:
            for path in firefox_paths:
                username = path.split("\\")[-8]
                cmd_command = ['lib\\sqlite\\sqlite3.exe', path, '.headers on', '.mode csv', f'.output ESTK_Extraction_{collected_system_name}/Results/Browser_Data/firefox_history_{username}.csv', 'SELECT * FROM MOZ_PLACES;' ]
                process = subprocess.run(cmd_command, shell=True)
                time.sleep(1)
                if process.returncode == 0:
                    pass
                else:
                    no_error_browser_data = False
                    browser_data_anim_stop_event.set()
                    browser_data_anim_thread.join()

        browser_data_anim_stop_event.set()
        browser_data_anim_thread.join()

    except Exception as e:
        no_error_browser_data = False
        browser_data_anim_stop_event.set()
        browser_data_anim_thread.join()

def jumplist():
    global no_error_jumplist
    cmd_command = ['lib\\JLECmd.exe', '-q', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Jumplists-CustomDestinations', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Jumplist', '>', 'NUL']
    jumplist_anim_thread = threading.Thread(target=jumplist_anim)
    jumplist_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            cmd_command = ['lib\\JLECmd.exe', '-q', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Jumplists-AutomaticDestinations', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Jumplist', '>', 'NUL']
            try:
                process = subprocess.run(cmd_command, shell=True)
                if process.returncode == 0:
                    jumplist_anim_stop_event.set()
                    jumplist_anim_thread.join()
                else:
                    no_error_jumplist = False
                    jumplist_anim_stop_event.set()
                    jumplist_anim_thread.join()
            except Exception as e:
                no_error_jumplist = False
                jumplist_anim_stop_event.set()
                jumplist_anim_thread.join()
        else:
            no_error_jumplist = False
            jumplist_anim_stop_event.set()
            jumplist_anim_thread.join()
    except Exception as e:
        no_error_jumplist = False
        jumplist_anim_stop_event.set()
        jumplist_anim_thread.join()

def mft():
    global no_error_mft
    cmd_command = ['lib\\MFTECmd.exe', '-f', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\MFT\\C\\$MFT', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\MFT']
    mft_anim_thread = threading.Thread(target=mft_anim)
    mft_anim_thread.start()

    try:
        process = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.wait()
        if process.returncode == 0:
            mft_anim_stop_event.set()
            mft_anim_thread.join()
        else:
            no_error_mft = False
            mft_anim_stop_event.set()
            mft_anim_thread.join()
    except Exception as e:
        no_error_mft = False
        mft_anim_stop_event.set()
        mft_anim_thread.join()

def usnlog():
    global no_error_usnlog
    os.mkdir(f"ESTK_Extraction_{collected_system_name}\\Results\\UsnJournalandLogFile")
    cmd_command = ['lib\\NTFSLogTracker\\NTFS_Log_Tracker.exe', '-l', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\MISC\\C\\$LogFile', '-u', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\MISC\\C\\$Extend\\$J', '-m', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\MFT\\C\\$MFT', '-o', f'ESTK_Extraction_{collected_system_name}\\Results\\UsnJournalandLogFile', '-c', '>', 'NUL']
    usnlog_anim_thread = threading.Thread(target=usnlog_anim)
    usnlog_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            usnlog_anim_stop_event.set()
            usnlog_anim_thread.join()
        else:
            no_error_usnlog = False
            usnlog_anim_stop_event.set()
            usnlog_anim_thread.join()
    except Exception as e:
        no_error_usnlog = False
        usnlog_anim_stop_event.set()
        usnlog_anim_thread.join()

def prefetch():
    global no_error_prefetch
    cmd_command = ['lib\\PECmd.exe', '-q', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Prefetch_Files', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Prefetch_Files', '>', 'NUL']
    prefetch_anim_thread = threading.Thread(target=prefetch_anim)
    prefetch_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            prefetch_anim_stop_event.set()
            prefetch_anim_thread.join()
        else:
            no_error_prefetch = False
            prefetch_anim_stop_event.set()
            prefetch_anim_thread.join()
    except Exception as e:
        no_error_prefetch = False
        prefetch_anim_stop_event.set()
        prefetch_anim_thread.join()

def recent_files():
    global no_error_recent_files
    cmd_command = ['lib\\LECmd.exe', '-q', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Recent_Files', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Recent_Files', '>', 'NUL']
    recent_files_anim_thread = threading.Thread(target=recent_files_anim)
    recent_files_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            recent_files_anim_stop_event.set()
            recent_files_anim_thread.join()
        else:
            no_error_recent_files = False
            recent_files_anim_stop_event.set()
            recent_files_anim_thread.join()
    except Exception as e:
        no_error_recent_files = False
        recent_files_anim_stop_event.set()
        recent_files_anim_thread.join()

def recycle_bin():
    global no_error_recycle_bin
    cmd_command = ['lib\\RBCmd.exe', '-q', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Recycle_Bin', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Recycle_Bin', '>', 'NUL']
    recycle_bin_anim_thread = threading.Thread(target=recycle_bin_anim)
    recycle_bin_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            recycle_bin_anim_stop_event.set()
            recycle_bin_anim_thread.join()
        else:
            no_error_recent_files = False
            recycle_bin_anim_stop_event.set()
            recycle_bin_anim_thread.join()
    except Exception as e:
        no_error_recent_files = False
        recycle_bin_anim_stop_event.set()
        recycle_bin_anim_thread.join()

def shellbags():
    global no_error_shellbags
    cmd_command = ['lib\\SBECmd.exe', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Shellbags', '>', 'NUL']
    shellbags_anim_thread = threading.Thread(target=shellbags_anim)
    shellbags_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            shellbags_anim_stop_event.set()
            shellbags_anim_thread.join()
        else:
            no_error_shellbags = False
            shellbags_anim_stop_event.set()
            shellbags_anim_thread.join()
    except Exception as e:
        no_error_shellbags = False
        shellbags_anim_stop_event.set()
        shellbags_anim_thread.join()

def registry():
    global no_error_registry
    os.mkdir(f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives')
    cmd_command = ['python', '-W', 'ignore', 'lib\\RegRipper\\autoripy.py', 'lib\\Regripper\\', '-s', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Registry_Hives\\C\\Windows\\system32\\config', '-a', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Amcache\\C\\Windows\\AppCompat\\Programs\\', '-n', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\NTUSER.DAT\\', '-u', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\UsrClass.dat\\', '-r', f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives', '>', 'NUL']
    registry_anim_thread = threading.Thread(target=registry_anim)
    registry_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        cmd_commands = [['lib\\RegRipper\\rip.exe', '-r', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Registry_Hives\\C\\Windows\\system32\\config\\SOFTWARE', '-a', '>', f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives\\SOFTWARE.txt'], ['lib\\RegRipper\\rip.exe', '-r', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Registry_Hives\\C\\Windows\\system32\\config\\SAM', '-a', '>', f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives\\SAM.txt'], ['lib\\RegRipper\\rip.exe', '-r', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Registry_Hives\\C\\Windows\\system32\\config\\SYSTEM', '-a', '>', f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives\\SYSTEM.txt']]
        for cmd_command in cmd_commands:
            process = subprocess.run(cmd_command, shell=True)
        result = find_files(f"ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\NTUSER.DAT\\C\\Users", "NTUSER.DAT")
        for path in result:
            user = path.split("\\")[-2]
            cmd_command = ['lib\\RegRipper\\rip.exe', '-r', path, '-a', '>', f'ESTK_Extraction_{collected_system_name}\\Results\\Registry_Hives\\NTUSER_{user}.txt']
            process = subprocess.run(cmd_command, shell=True)
        registry_anim_stop_event.set()
        registry_anim_thread.join()
    except Exception as e:
        no_error_registry = False
        registry_anim_stop_event.set()
        registry_anim_thread.join()

def event_logs():
    global no_error_event_logs
    os.mkdir(f"ESTK_Extraction_{collected_system_name}\\Results\\Windows_Event_Logs")
    cmd_command = ['python', '-W', 'ignore', 'lib\\APT-Hunter\\APT-Hunter.py', '-p', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Windows_Event_Logs', '-o', 'APT-Hunter', '-allreport', '>', 'NUL']
    event_logs_anim_thread = threading.Thread(target=event_logs_anim)
    event_logs_anim_thread.start()

    try:
        process = subprocess.run(cmd_command, shell=True)
        if process.returncode == 0:
            shutil.move('APT-Hunter', f'ESTK_Extraction_{collected_system_name}\\Results\\Windows_Event_Logs')
            cmd_command = ['lib\\EvtxeCmd\\EvtxECmd.exe', '-d', f'ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Windows_Event_Logs', '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\Windows_Event_Logs', '>', 'NUL']
            process = subprocess.run(cmd_command, shell=True)
            if process.returncode == 0:
                event_logs_anim_stop_event.set()
                event_logs_anim_thread.join()
            else:
                no_error_event_logs = False
                event_logs_anim_stop_event.set()
                event_logs_anim_thread.join()
        else:
            no_error_event_logs = False
            event_logs_anim_stop_event.set()
            event_logs_anim_thread.join()
    except Exception as e:
        no_error_event_logs = False
        event_logs_anim_stop_event.set()
        event_logs_anim_thread.join()

def windows_timeline():
    global no_error_windows_timeline
    result = find_files(f"ESTK_Extraction_{collected_system_name}\\ESLCK_Collection\\Collection\\Artifacts\\Saved_Files\\Windows_Timeline", "ActivitiesCache.db")
    windows_timeline_anim_thread = threading.Thread(target=windows_timeline_anim)
    windows_timeline_anim_thread.start()
    for path in result:
        cmd_command = ['lib\\WxTCmd.exe', '-f', path, '--csv', f'ESTK_Extraction_{collected_system_name}\\Results\\WindowsTimeline', '>', 'NUL']
        try:
            process = subprocess.run(cmd_command, shell=True)
            if process.returncode == 0:
                windows_timeline_anim_stop_event.set()
                windows_timeline_anim_thread.join()
            else:
                no_error_windows_timeline = False
                windows_timeline_anim_stop_event.set()
                windows_timeline_anim_thread.join()
        except Exception as e:
            no_error_windows_timeline = False
            windows_timeline_anim_stop_event.set()
            windows_timeline_anim_thread.join()

if __name__ == "__main__":
    set_cmd_title("WAP - Windows Artifact Parser")
    check_admin_rights()

    zip_file_path, directory, password = None, None, None

    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', help="Path to the artifact zip")
    parser.add_argument('--directory', help="Path to the artifacts directory")
    parser.add_argument('--password', help="Password for the zip file, if it's password-protected")

    args = parser.parse_args()

    if args.directory and args.zip:
        print("[ERROR] Either --zip or --directory must be provided not both.")
        print("Press any key to exit...")
        msvcrt.getch()
        sys.exit(1)
    if args.directory or args.zip:
        if args.zip and not args.password:
            y_n = input("Is the zip password protected? [y/N] :: ")
            if y_n in ["y", "Y"]:
                print("[INFO] Run the script with --password [PASSWORD] along with --zip.")
                print("Press any key to exit...")
                msvcrt.getch()
                sys.exit(1)
            if y_n in ["n", "", "N"]:
                zip_file_path = args.zip
            else:
                print("[ERROR] Please select Y or N")
                print("Press any key to exit...")
                msvcrt.getch()
                sys.exit(1)
        if args.zip and args.password:
            zip_file_path = args.zip
            zip_password = args.password
        if args.directory:
            directory = args.directory
    else:
        print("[ERROR] Either --zip or --directory must be provided.")
        print("Press any key to exit...")
        msvcrt.getch()
        sys.exit(1)

    print_wap_banner()
    start_time = time.time()

    if zip_file_path:
        print("Processing:", zip_file_path)
        print("Started at:", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("---------------------------------------")
        print("[INFO] Started Unzipping Module")
        unzip_directory(zip_file_path, password)
        time.sleep(1)
        os.mkdir("WAP_Extraction\\Results")
    else:
        print("Processing:", directory)
        print("Started at:", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("---------------------------------------")
        os.mkdir("Results")
    #############################################################################
    # print("[INFO] Started Amcache Parser Module")
    # amcache()
    # time.sleep(1)
    #
    # print("[INFO] Started Browser History Parser Module")
    # browser_data()
    # time.sleep(1)
    #
    # print("[INFO] Started Jumplist Parser Module")
    # jumplist()
    # time.sleep(1)
    #
    # print("[INFO] Started $MFT Parser Module")
    # mft()
    # time.sleep(1)
    #
    # print("[INFO] Started UsnJournal & $LogFile Parser Module")
    # usnlog()
    # time.sleep(1)
    #
    # print("[INFO] Started Prefetch Files Parser Module")
    # prefetch()
    # time.sleep(1)
    #
    # print("[INFO] Started Recent Files Parser Module")
    # recent_files()
    # time.sleep(1)
    #
    # print("[INFO] Started Recycle Bin Files Parser Module")
    # recycle_bin()
    # time.sleep(1)
    #
    # print("[INFO] Started Shellbags Parser Module")
    # shellbags()
    # time.sleep(1)
    #
    # print("[INFO] Started Registry Parser Module")
    # registry()
    # time.sleep(1)
    #
    # print("[INFO] Started Windows Event Logs Parser Module")
    # event_logs()
    # time.sleep(1)
    #
    # print("[INFO] Started Windows Timeline Database Parser Module")
    # windows_timeline()
    #
    # end_time = time.time()
    #
    # elapsed_time_seconds = end_time - start_time
    # hours, remainder = divmod(elapsed_time_seconds, 3600)
    # minutes, seconds = divmod(remainder, 60)
    # formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    # print(f"\nProgram execution time: {formatted_time}\n")
    #
    # print("Parsing Successfull. You can now close the window...")
