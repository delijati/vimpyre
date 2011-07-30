#!/usr/bin/env python
# coding: utf-8

import shutil
import sys
import urllib
from os import listdir, path, system

import lxml.html as lhtml
import simplejson

import util
from util import console

class Bat(object):

    CURR_SCRIPT = ''
    GITHUB_VIM_REPO = 'http://github.com/api/v2/json/repos/watched/vim-scripts'
    PATHOGEN_URL = 'http://github.com/vim-scripts/pathogen.vim/raw/master/plugin/pathogen.vim'
    VIM_PATH = path.join(path.expanduser('~'), '.vim')
    AUTOLOAD_PATH = path.join(VIM_PATH, 'autoload')
    VIMPYRE_PATH = path.join(VIM_PATH, 'vimpyre')
    VIMPYRE_DB_PATH = path.join(VIM_PATH, 'vimpyre.json')

    def __init__(self, script = ''):
        self.CURR_SCRIPT = script

    def install_base(self):
        """
        Install pathogen.vim and create vimpyre directory.

            >>> bat = Bat()
            >>> bat.install_base()
            => => Send a bat to catch pathogen.vim ...
            Catch done! Please add the following message to your .vimrc:
            call pathogen#runtime_append_all_bundles("vimpyre")
        """
        try:
            console('=> => Send a bat to catch pathogen.vim ...')
            raw_urlopen = urllib.urlopen(self.PATHOGEN_URL)
            if raw_urlopen.getcode() == 200:
                util.mkdir_p(self.AUTOLOAD_PATH)
                util.mkdir_p(self.VIMPYRE_PATH)
                raw_pathogen = raw_urlopen.read()
                pathogen = path.join(self.AUTOLOAD_PATH, 'pathogen.vim')
                with open(pathogen, 'w') as f:
                    f.write(raw_pathogen)
                console('Catch done! Please add the following to your .vimrc:')
                console('call pathogen#runtime_append_all_bundles("vimpyre")')
            else:
                console('Catch fail! Please try again!')
        except:
            console('[Unexpected Error] Catch fail! Please try again!')

    def syncdb(self):
        """
        Fetch http://github.com/api/v2/json/repos/show/vim-scripts

            >>> bat = Bat('')
            >>> bat.syncdb()
            => => Send a bat to sync vim-scripts repo ...
            Sync repo done!
        """
        try:
            console('=> => Send a bat to sync vim-scripts repo ...')
            raw_urlopen = urllib.urlopen(self.GITHUB_VIM_REPO)
            if raw_urlopen.getcode() == 200:
                raw_json = raw_urlopen.read()
                with open(self.VIMPYRE_DB_PATH, 'w') as f:
                    f.write(raw_json)
                console('Sync repo done!')
            else:
                console('Sync repo fail! Please try again!')
        except:
            console('[Unexpected Error] Sync repo fail! Please try again')

    def install(self):
        console('=> => Send a bat to catch %s' % self.CURR_SCRIPT)
        try:
            ret = self._check_name()
            if ret:
                cmd_fetch = 'git clone --depth 1 %s' % (ret['url'] + '.git')
                util.mkdir_p(self.VIMPYRE_PATH)
                with util.cd(self.VIMPYRE_PATH):
                    system(cmd_fetch)
            else:
                msg = ('%s not found! Please use `vimpyre search <vim-script>`'
                       ' to check the script name and install again!' %
                       self.CURR_SCRIPT)
                console(msg)
        except:
            self.install_base()
            self.syncdb()

    def update(self):
        console('=> => Send a bat to update %s' % self.CURR_SCRIPT)
        bundle_path = path.join(self.VIMPYRE_PATH, self.CURR_SCRIPT)
        if path.isdir(bundle_path):
            with util.cd(bundle_path):
                system('git pull')
            console('%s update done!' % self.CURR_SCRIPT)
        else:
            console('%s does not exist!' % self.CURR_SCRIPT)

    def update_all(self):
        console('=> => Send bats to update all installed vim-scripts ...')
        try:
            rets = listdir(self.VIMPYRE_PATH)
            if rets:
                for item in rets:
                    console('=> Update %s ...' % item)
                    with util.cd(path.join(self.VIMPYRE_PATH, item)):
                        system('git pull')
                console('Update all vim-scripts done!')
            else:
                console('No vim-scripts! Please use `vimpyre install <vim-scripts>` first!')
        except OSError:
            console('Cannot access your vimpyre path!')
            console('Please use `vimpyre init; vimpyre syncdb; vimpyre install <vim-scripts>` first!')
        except:
            console('[Unexpected Error] Please try again!')

    def remove(self):
        console('=> => Send a bat to bite %s' % self.CURR_SCRIPT)
        bundle_path = path.join(self.VIMPYRE_PATH, self.CURR_SCRIPT)
        if self._check_name() and path.isdir(bundle_path):
            shutil.rmtree(bundle_path)
            console('%s removed!' % self.CURR_SCRIPT)
        else:
            console('%s does not exist!' % self.CURR_SCRIPT)

    def remove_all(self):
        console('=> => Send bats to clean all vimpyre files')
        bundles_dir = self.VIMPYRE_PATH
        try:
            with util.cd(bundles_dir):
                bundles = [bundle for bundle in listdir('.') if
                           path.isdir(bundle)]
                for bundle in bundles:
                    shutil.rmtree(bundle)
            console('Remove vimpyre bundles done!')
        except OSError:
            console('Could not remove bundles! Does your vimpyre directory '
                  'exist and have proper permissions?')
        else:
            console('Please remove %s/pathogen.vim manually and clean `call pathogen#runtime_append_all_bundles("vimpyre")` from your .vimrc!' % self.AUTOLOAD_PATH)
            console('')
            console('If you wish to use vimpyre to manage your vim scripts again, you need to use `vimpyre init; vimpyre syncdb` first!')

    def list_installed(self):
        console('=> => Send bats to collect all your vim-scripts')
        if path.isdir(self.VIMPYRE_PATH):
            rets = listdir(self.VIMPYRE_PATH)
            if rets:
                try:
                    repo = simplejson.loads(open(self.VIMPYRE_DB_PATH,'r').read())
                    db_items = repo['repositories']
                    for item in rets:
                        for db_item in db_items:
                            if item == db_item['name']:
                                console('\033[1m%s\033[m => %s' % (db_item['name'].encode('utf-8'), db_item['description'].encode('utf-8')))
                                found = True
                                break
                            else:
                                found = False

                        if not found:
                            console('\033[1m%s\033[m' % item.encode('utf-8'))
                except:
                    console('Please use `vimpyre init; vimpyre syncdb; vimpyre install <vim-scripts>` first!')
            else:
                console('No vim-scripts found!')
        else:
            console('Please use `vimpyre init; vimpyre syncdb; vimpyre install <vim-scripts>` first!')

    def _check_name(self):
        try:
            search_ret = self.search()
            rets = [item for item in search_ret if self.CURR_SCRIPT == item['name']]
            if rets:
                return rets[0]
            return []
        except:
            pass

    def list_all(self):
        try:
            repo = simplejson.loads(open(self.VIMPYRE_DB_PATH,'r').read())
            db_items = repo['repositories']
            if db_items:
                for item in db_items:
                    if path.isdir(path.join(self.VIMPYRE_PATH, item['name'])):
                        console('%s => %s [installed]' % (item['name'].encode('utf-8'), item['description'].encode('utf-8')))
                    else:
                        console('%s => %s' % (item['name'].encode('utf-8'), item['description'].encode('utf-8')))
            else:
                console('Please use `vimpyre syncdb` first and try again!')
        except:
            raise

    def search(self):
        """
        Search github vim-scripts, return array.

            >>> bat = Bat('xxxxxxxx')
            >>> bat.search()
            []
            >>> bat = Bat('pathogen')
            >>> bat.search() # doctest: +ELLIPSIS
            [{..., 'name': 'pathogen.vim'}]
        """
        try:
            repo = simplejson.loads(open(self.VIMPYRE_DB_PATH,'r').read())
            db_items = repo['repositories']
            if db_items:
                return [item for item in db_items if self.CURR_SCRIPT.lower() in item['name'].lower() or self.CURR_SCRIPT.lower() in item['description'].lower()]
        except:
            pass
