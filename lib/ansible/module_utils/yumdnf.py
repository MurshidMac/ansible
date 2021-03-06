# -*- coding: utf-8 -*-
#
# # Copyright: (c) 2012, Red Hat, Inc
# Written by Seth Vidal <skvidal at fedoraproject.org>
# Contributing Authors:
#    - Ansible Core Team
#    - Eduard Snesarev (@verm666)
#    - Berend De Schouwer (@berenddeschouwer)
#    - Abhijeet Kasurde (@Akasurde)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import tempfile
from abc import ABCMeta, abstractmethod

from ansible.module_utils._text import to_native
from ansible.module_utils.six import with_metaclass

yumdnf_argument_spec = dict(
    argument_spec=dict(
        allow_downgrade=dict(type='bool', default=False),
        autoremove=dict(type='bool', default=False),
        bugfix=dict(required=False, type='bool', default=False),
        conf_file=dict(type='str'),
        disable_excludes=dict(type='str', default=None, choices=['all', 'main', 'repoid']),
        disable_gpg_check=dict(type='bool', default=False),
        disable_plugin=dict(type='list', default=[]),
        disablerepo=dict(type='list', default=[]),
        download_only=dict(type='bool', default=False),
        enable_plugin=dict(type='list', default=[]),
        enablerepo=dict(type='list', default=[]),
        exclude=dict(type='list', default=[]),
        installroot=dict(type='str', default="/"),
        install_repoquery=dict(type='bool', default=True),
        list=dict(type='str'),
        name=dict(type='list', aliases=['pkg'], default=[]),
        releasever=dict(default=None),
        security=dict(type='bool', default=False),
        skip_broken=dict(type='bool', default=False),
        # removed==absent, installed==present, these are accepted as aliases
        state=dict(type='str', default='present', choices=['absent', 'installed', 'latest', 'present', 'removed']),
        update_cache=dict(type='bool', default=False, aliases=['expire-cache']),
        update_only=dict(required=False, default="no", type='bool'),
        validate_certs=dict(type='bool', default=True),
        # this should not be needed, but exists as a failsafe
    ),
    required_one_of=[['name', 'list']],
    mutually_exclusive=[['name', 'list']],
    supports_check_mode=True,
)


class YumDnf(with_metaclass(ABCMeta, object)):
    """
    Abstract class that handles the population of instance variables that should
    be identical between both YUM and DNF modules because of the feature parity
    and shared argument spec
    """

    def __init__(self, module):

        self.module = module

        self.allow_downgrade = self.module.params['allow_downgrade']
        self.autoremove = self.module.params['autoremove']
        self.bugfix = self.module.params['bugfix']
        self.conf_file = self.module.params['conf_file']
        self.disable_excludes = self.module.params['disable_excludes']
        self.disable_gpg_check = self.module.params['disable_gpg_check']
        self.disable_plugin = self.module.params['disable_plugin']
        self.disablerepo = self.module.params.get('disablerepo', [])
        self.download_only = self.module.params['download_only']
        self.enable_plugin = self.module.params['enable_plugin']
        self.enablerepo = self.module.params.get('enablerepo', [])
        self.exclude = self.module.params['exclude']
        self.installroot = self.module.params['installroot']
        self.install_repoquery = self.module.params['install_repoquery']
        self.list = self.module.params['list']
        self.names = [p.strip() for p in self.module.params['name']]
        self.releasever = self.module.params['releasever']
        self.security = self.module.params['security']
        self.skip_broken = self.module.params['skip_broken']
        self.state = self.module.params['state']
        self.update_only = self.module.params['update_only']
        self.update_cache = self.module.params['update_cache']
        self.validate_certs = self.module.params['validate_certs']

        # It's possible someone passed a comma separated string since it used
        # to be a string type, so we should handle that
        self.names = self.listify_comma_sep_strings_in_list(self.names)
        self.disablerepo = self.listify_comma_sep_strings_in_list(self.disablerepo)
        self.enablerepo = self.listify_comma_sep_strings_in_list(self.enablerepo)
        self.exclude = self.listify_comma_sep_strings_in_list(self.exclude)

    def listify_comma_sep_strings_in_list(self, some_list):
        """
        method to accept a list of strings as the parameter, find any strings
        in that list that are comma separated, remove them from the list and add
        their comma separated elements to the original list
        """
        new_list = []
        remove_from_original_list = []
        for element in some_list:
            if ',' in element:
                remove_from_original_list.append(element)
                new_list.extend([e.strip() for e in element.split(',')])

        for element in remove_from_original_list:
            some_list.remove(element)

        some_list.extend(new_list)

        return some_list

    @abstractmethod
    def run(self):
        raise NotImplementedError
