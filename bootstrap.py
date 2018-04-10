#!/usr/bin/env python

import os
import argparse
import subprocess
import logging

def main(args):
    print(args)

    createdir(args.envdir)

    #Install Python with --prefix=<args.envdir>
    install_python(args.pythontar, args.envdir)

    #Append <args.envdir>/bin to the PATH environment variable
    prepend_to_path(args.envdir+"/bin")

    #Install Virtualenv
    install_virtualenv(args.venvtar, args.envdir)

    #Create a virtualenv at <args.pythonenv>
    cmd_activate = create_virtualenvironment(args.pythonenv)


def createdir(dir_):
    try:
        os.makedirs(dir_)
    except OSError as e:
        print(e)

def prepend_to_path(p):
    """ Prepends p to the PATH environment variable. """
    os.environ["PATH"] = p+":"+os.environ["PATH"]

def unpack(tarfile, targetdir):
    subprocess.call(['tar', '-xf', tarfile, '-C', targetdir])

def install_python(pythontar, envdir):
    unpack(pythontar, envdir)
    with CD(envdir+'/'+pythontar.rstrip('.tar.xz')):
        #Assumes top directory is Python-2.7.10 if
        #file is named Python-2.7.10.tar.xz
        subprocess.call(['./configure', '--prefix='+envdir])
        subprocess.call(['make'])
        subprocess.call(['make', 'install'])

def install_virtualenv(venvtar, envdir):
    unpack(venvtar, envdir)
    with CD(envdir+'/'+venvtar.rstrip('.tar.gz')):
        #Assumes top directory is virtualenv-12.1.1 if
        #file is named virtualenv-12.1.1.tar.gz
        subprocess.call(['python', 'setup.py', 'install'])

def create_virtualenvironment(path):
    subprocess.call(['virtualenv', path])
    cmd_activate = "'source "+path+"/bin/./activate'"
    print("\nTo activate the virtual environment, run: %s"%cmd_activate)
    print("\nTo deactivate an activated virtual environment, run: deactivate")
    return cmd_activate

def append_line_to_file(filepath, line):
    assert isinstance(line, str)
    assert os.path.exists(filepath)
    cmd1 = "echo '#Added by bootstrap.py' >> "+str(filepath),
    cmd2 = "echo "+line+" >> "+str(filepath)
    subprocess.call(cmd1, shell=True)
    subprocess.call(cmd2, shell=True)

def list_shell_rcfiles():
    rcfiles = []
    home = os.environ["HOME"]

    #for now, only support bash/zsh syntax, later add csh/tcsh
    rcs = [".bashrc", ".zshrc"]
    for rc in rcs:
        path_to_rcfile = home+"/"+rc
        if os.path.exists(path_to_rcfile):
            rcfiles.append(path_to_rcfile)

    return rcfiles


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pythontar', '-p', required=True,
                        help="python source tarball")
    parser.add_argument('--venvtar', '-v', required=True,
                        help="virtualenv source tarball")
    parser.add_argument('--envdir', '-e', required=True,
                        help="destination environment, will be created\
                        if path doesn't exist.")
    parser.add_argument('--pythonenv', '-n', required=True,
                        help="destination directory for your virtual env")
    #check if you need to remove trailing / from pythonenv
    args = parser.parse_args()
    args.pythonenv = args.pythonenv.rstrip('/')
    args.envdir = args.envdir.rstrip('/')
    return args

class CD(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, extype, exvalue, traceback):
        os.chdir(self.cwd)

if __name__ == "__main__":
    main(get_args())

