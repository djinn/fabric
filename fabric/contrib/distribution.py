#--
#@(#)distribution.py
#
# distribution
# Copyright(c) 2011 Supreet Sethi <supreet.sethi@gmail.com> 
"""
Module provides simple API for remote host details and package management.
"""



from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import *
from os import tmpnam

def host_details(use_sudo=False, verbose=False):
    with hide('running', 'stdout', 'stderr'):
        plt = first('/etc/lsb-release', '/etc/redhat-release', '/etc/debian_version', use_sudo=use_sudo)
        distro_arch = run('uname -m')
        distro = 'Unknown'
        version = 'Unknown'
        extra = 'Unknown'
        compatible = 'Unknown'
        if distro_arch.endswith('86'):
            distro_arch = 'i386'
        if plt == '/etc/debian_version':
            distro = 'debian'
            version = run('cat /etc/debian_version')
            extra = ''
            compatible = 'deb'
            if distro_arch == 'x86_64':
                distro_arch = 'amd64'
            
        elif plt == '/etc/lsb-release':
            distro = run('lsb_release -i').split(':')[1].strip()
            version = run('lsb_release -r').split(':')[1].strip()
            extra = run('lsb_release -c').split(':')[1].strip()
            compatible = 'deb'
            if distro_arch == 'x86_64':
                distro_arch = 'amd64'
        elif plt == '/etc/redhat-release':
            pd = run('cat /etc/redhat-release')
            try:
                distro, lnx, release, version, extra = pd.split(' ')
            except:
                distro, release, version, extra = pd.split(' ')
            extra = extra[1:-1]
            compatible = 'rpm'
        return distro, version , extra, distro_arch, compatible

def check_pkg_installed(*args, **kwargs):
    distro, version, extra, distro_arch, compatible = host_details(*kwargs)
    pkg_dict = {}
    with hide('running', 'stdout', 'stderr'):
    
        if compatible == 'deb':
            for arg in args:
                with settings(warn_only=True):
                    dt = run('dpkg -l %s' % arg)
                    if dt.startswith("No packages"):
                        pkg_dict[arg] = False
                    else:
                        pkg_dict[arg] = True
        if compatible == 'rpm':
            for arg in args:
                dt = run('rpm -qa %s' % arg)
                if len(dt) > 0:
                    pkg_dict[arg] = True
                else: 
                    pkg_dict[arg] = False


        return pkg_dict

def pkg_install(use_sudo=True):
    pass


def download(uri, dest=None, use_sudo=False):
    with hide('running', 'stdout', 'stderr'):
        pkg_list = check_pkg_installed('curl')
        if pkg_list['curl'] == False:
            pkg_install('curl')
        if dest == None:
            dest = os.tmpnam()
        run('curl %s > %s' % (uri, dest))
        return dest
