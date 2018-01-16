# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import urllib.request
import urllib.parse
import json
import logging
import os
import yaml

from .fileset import FileSet

class ZanataFileSet(FileSet):

    username = None
    auth = None

    def _set_auth_api_token(self):
        try:
            with open("../cfg/credentials/zanata.yaml", "r") as stream:
                values = yaml.load(stream)
                for value in values:
                    if self.project_name not in value:
                        continue

                    self.username = value[self.project_name]['username']
                    self.auth = value[self.project_name]['auth-token']

            if self.username is None or self.auth is None:
                msg = 'zenata.set_auth_api_token: No user or auth token'
                logging.error(msg)

        except Exception as detail:
            msg = 'ZanataFileSet._set_auth_api_token: {0}'.format(str(detail))
            logging.error(msg)

    def _get_projects_ids(self):
        url = urllib.parse.urljoin(self.url, "/rest/projects")
        headers = {'accept': 'application/json'}

        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        response_text = response.read().decode(response.info().get_param('charset') or 'utf-8')
        projects = json.loads(response_text)
        ids = []
        for project_dict in projects:
            ids.append(project_dict['id'])

        return ids

    def _get_tmx_file(self, project_id):
        req = "/rest/tm/projects/{0}/?locale=ca".format(project_id)
        url = urllib.parse.urljoin(self.url, req)
        headers = {'X-Auth-User': self.username, 'X-Auth-Token': self.auth}

        try:
            filename = '{0}-ca.tmx'.format(project_id)
            filename = os.path.join(self.temp_dir, filename)
            req = urllib.request.Request(url, headers=headers)

            msg = 'Download file \'{0}\' to {1}'.format(url, filename)
            logging.info(msg)

            infile = urllib.request.urlopen(req)
            output = open(filename, 'wb')
            output.write(infile.read())
            output.close()

        except Exception as detail:
            logging.error("ZanataFileSet._get_tmx_file {0} - error: {1}".format(url, detail))

    def do(self):
        self._set_auth_api_token()
        project_ids = self._get_projects_ids()
        for project_id in project_ids:
            self._get_tmx_file(project_id)

        self.build()
