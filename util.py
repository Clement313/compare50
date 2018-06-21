import os

from flask import has_app_context

from celery import Celery
from backports.shutil_which import which
from tempfile import gettempdir, mkstemp
from werkzeug.utils import secure_filename

import patoolib


# Supported archives, per https://github.com/wummel/patool
ARCHIVES = [".bz2", ".tar", ".tar.gz", ".tgz", ".zip", ".7z", ".xz"]


# Supported helper applications
HELPERS = {
    "7z": [".7z"],
    "compress": [".z"],
    "unrar": [".rar"],
    "xz": [".xz"]
}


for progname, extensions in HELPERS.items():
    if which(progname):
        ARCHIVES.extend(extensions)


# Run celery tasks in Flask context
# https://stackoverflow.com/questions/12044776/how-to-use-flask-sqlalchemy-in-a-celery-task
class FlaskCelery(Celery):
    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config)


def save(file, dirpath):
    """Saves file at dirpath, extracting to identically named folder if archive."""
    filename = secure_filename(file.filename)
    path = os.path.join(dirpath, filename)
    if path.lower().endswith(tuple(ARCHIVES)):
        try:
            _, pathname = mkstemp(filename)
            file.save(pathname)
            os.mkdir(path)
            try:
                patoolib.extract_archive(pathname, outdir=path)
                print("Extracted!")
            except patoolib.util.PatoolError:
                abort(500) # TODO: pass helpful message
            os.remove(pathname)
        except Exception:
            abort(500) # TODO: pass helpful message
    else:
        file.save(path)


def ignored(path):
    """Returns whether the given path ends in an ignored name."""
    ignored_prefixes = [".", "__"]
    name = os.path.basename(path)
    return any(name.startswith(p) for p in ignored_prefixes)


def walk(directory):
    """Walks directory recursively, returning sorted list of paths of files therein."""
    files = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        if ignored(dirpath):
            continue
        for filename in filenames:
            if ignored(filename):
                continue
            files.append(os.path.join(dirpath, filename))
    sorted(sorted(files), key=str.upper)
    return files


def walk_submissions(directory):
    """Walks directory recursively, returning a list of submissions that are lists of files."""
    for (dirpath, dirnames, filenames) in os.walk(directory):
        if ignored(dirpath):
            continue
        dirnames = [d for d in dirnames if not ignored(d)]
        filenames = [f for f in filenames if not ignored(f)]
        print(f"Walking {dirpath}, dirs={dirnames}, files={filenames}")
        if len(filenames) > 0:
            # single submission
            return [tuple(sorted([os.path.join(dirpath, f)
                                  for f in filenames]))]
        if len(dirnames) > 1:
            # multiple submissions, each in own subdirectory
            return [tuple(walk(os.path.join(dirpath, d))) for d in dirnames]


def submission_path(files):
    """Given a list of files in a submission, return the submission's path"""
    if len(files) == 1:
        return os.path.dirname(files[0])
    else:
        return os.path.commonpath(files)
