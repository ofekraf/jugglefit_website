from pathlib import Path
from pylib.consts import (
    TRICK_SUGGESTIONS_BRANCH_NAME, TRICK_SUGGESTIONS_FOLDER, TRICK_SUGGESTIONS_PROP_FILE_MAP
)
from pylib.classes.prop import Prop
from git import GitCommandError
from pylib.globals import git_mutex, jugglefit_bot_repo, GIT_REMOTE_NAME, GIT_MAIN_BRANCH
from pylib.utils.general import acquired


def get_trick_suggestion_file(prop) -> Path:
    return TRICK_SUGGESTIONS_FOLDER / TRICK_SUGGESTIONS_PROP_FILE_MAP[prop]

def add_trick_suggestion(*, prop, trick):
    """Add a trick suggestion to the appropriate file and commit it to git.
    
    Args:
        prop: The prop type for the trick
        trick: The trick to add
        
    Raises:
        GitCommandError: If any git operation fails
    """
    target_file = get_trick_suggestion_file(prop)
    
    with acquired(git_mutex):
        # Add the trick to the file
        with target_file.open('a', encoding='utf-8') as f:
            f.write(str(trick) + ',\n')
        
        try:
            # Store current branch
            current_branch = jugglefit_bot_repo.active_branch.name
            
            try:
                # Create and checkout suggestion branch
                if TRICK_SUGGESTIONS_BRANCH_NAME in jugglefit_bot_repo.heads:
                    jugglefit_bot_repo.heads[TRICK_SUGGESTIONS_BRANCH_NAME].checkout()
                    origin = jugglefit_bot_repo.remote(GIT_REMOTE_NAME)
                    origin.pull(TRICK_SUGGESTIONS_BRANCH_NAME)
                else:
                    jugglefit_bot_repo.create_head(TRICK_SUGGESTIONS_BRANCH_NAME).checkout()
                
                # Add and commit changes
                jugglefit_bot_repo.index.add([str(target_file)])
                commit_message = f"Add trick suggestion: {trick.name} for {prop.value}"
                jugglefit_bot_repo.index.commit(commit_message)
                
                # Push changes
                origin = jugglefit_bot_repo.remote(GIT_REMOTE_NAME)
                origin.push(TRICK_SUGGESTIONS_BRANCH_NAME, force=True)
                
            finally:
                # Always try to restore original branch
                try:
                    jugglefit_bot_repo.heads[current_branch].checkout()
                except (ValueError, GitCommandError):
                    # If we can't restore the original branch, try main
                    jugglefit_bot_repo.heads[GIT_MAIN_BRANCH].checkout()
            
        except GitCommandError as e:
            print(f"Error during git operations: {e}")
            raise
