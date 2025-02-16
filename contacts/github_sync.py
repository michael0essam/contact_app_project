import sqlite3
import logging
import requests
from github import Github, GithubException, UnknownObjectException
from contacts.models import PendingChange

# Configure logging to use errors.log for both error and info messages
logging.basicConfig(filename='logging.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_online():
    try:
        requests.head("https://github.com", timeout=1)
        return True
    except requests.ConnectionError:
        return False

# Personal Access Token for GitHub


# Repository name and file path in the repository
REPO_NAME = 'michael0essam/contacts-app'
FILE_PATH = 'changes.txt'
PC_NAME = "contacts_web_app"

def get_service():
    if not is_online():
        raise Exception("Offline")
    else:
        try:
            global g
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(REPO_NAME)
            return repo
        except UnknownObjectException:
            logging.error(f"Repository '{REPO_NAME}' not found. Please check the repository name.")
        except GithubException as e:
            logging.error(f"Error getting repository service: {e}")
            return None
        


def queue_change(query):
    if not is_online():
        try:
            # Save the query to the PendingChange table
            PendingChange.objects.create(query=query)
            logging.info(f"Successfully queued change: {query}")
        except Exception as e:
            logging.error(f"Failed to queue change: {e}")
    else:
        try:
            repo = get_service()
            contents = repo.get_contents(FILE_PATH)
            existing_data = contents.decoded_content.decode('utf-8')
            new_data = existing_data + "\n" + query
            commit_message = f"Updating the database by {PC_NAME}"
            repo.update_file(contents.path, commit_message, new_data, contents.sha)
            logging.info("queueing changes successfully.")
            print_rate_limit_status(g)
        except GithubException as e:
            logging.error(f"Error queuing change: {e}", exc_info=True)
            
def upload_offline_changes():
    try:
        repo = get_service()
        contents = repo.get_contents(FILE_PATH)
        existing_data = contents.decoded_content.decode('utf-8')

        # Retrieve all pending changes from the database
        pending_changes = PendingChange.objects.all()
        offline_data = "\n".join([change.query for change in pending_changes])

        combined_data = existing_data + "\n" + offline_data
        repo.update_file(contents.path, f"accessing the database by the Web APP", combined_data, contents.sha)
        print_rate_limit_status(g)
        # Clear the pending changes after successful upload
        PendingChange.objects.all().delete()

    except GithubException as e:
        logging.error(f"Error uploading offline changes: {e}", exc_info=True)


def download_changes():
    try:
        # Connect to GitHub repository
        repo = get_service()
        contents = repo.get_contents(FILE_PATH)
        downloaded_data = contents.decoded_content.decode('utf-8').splitlines()

        # Connect to SQLite database
        conn = sqlite3.connect("db.sqlite3")  # Use the Django SQLite database
        cursor = conn.cursor()

        # Execute each query from the downloaded data
        for query in downloaded_data:
            if not query.strip():  # Skip empty queries
                continue
            try:
                cursor.execute(query)
            except sqlite3.IntegrityError:
                # Ignore duplicate entries due to primary key constraints
                pass
            except sqlite3.OperationalError as e:
                # Log specific operational errors (e.g., missing table/column)
                if "no such table" in str(e) or "no column named" in str(e):
                    logging.error(f"Database schema issue: {e}")
                else:
                    raise e

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        # Clear the local changes file after successful execution
        open("changes.txt", "w", encoding="utf-8").close()

        # Log success message
        print_rate_limit_status(g)
    except GithubException as e:
        # Log GitHub-related errors
        logging.error(f"Error downloading changes: {e}", exc_info=True)
    except Exception as e:
        # Log any other unexpected errors
        logging.error(f"An error occurred during download: {e}", exc_info=True)

def print_rate_limit_status(g):
    rate_limit = g.get_rate_limit()
    core_rate = rate_limit.core
    log_message = (
        f"Core rate limit: {core_rate.limit}\n"
        f"Core requests remaining: {core_rate.remaining}\n"
        f"Core requests used: {core_rate.used}"
    )
    logging.info(log_message)