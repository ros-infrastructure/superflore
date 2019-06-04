# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict
import urllib

import bs4


class OpenEmbeddedLayersDB(object):
    def __init__(self):
        # Tells if we could read recipe information
        self._exists = False
        # OpenEmbedded branch to be queried
        self._oe_branch = 'thud'
        # Valid layers in priority order to filter when searching for a recipe
        self._prio_valid_layers = OrderedDict.fromkeys(
            ['openembedded-core', 'meta-oe', 'meta-python', 'meta-multimedia',
             'meta-ros', 'meta-intel-realsense', 'meta-qt5', 'meta-clang',
             'meta-sca', 'meta-openstack', 'meta-virtualization'])
        # All fields below come straight from OE Layer query table results
        self.name = ''
        self.version = ''
        self.summary = ''
        self.description = ''
        self.section = ''
        self.license = ''
        self.homepage = ''
        self.recipe = ''
        self.layer = ''
        self.inherits = ''
        self.dependencies = ''
        self.packageconfig = ''

    def __str__(self):
        if not self._exists:
            return ''
        return '\n'.join(
            [getattr(self, i) for i in vars(self) if not i.startswith('_')])

    def _fill_field(self, key, value):
        if key:
            my_attr = '{}'.format(key.split()[0].lower())
            if hasattr(self, my_attr):
                setattr(self, my_attr, value)
                return True
        return False

    def _get_first_on_multiple_matches(self, bs):
        class QueryResult:
            def __init__(self):
                self.recipe_name = ''
                self.link = ''
                self.version = ''
                self.description = ''
                self.layer = ''

            def __str__(self):
                return '\n'.join([self.recipe_name, self.link, self.version,
                                  self.description, self.layer])

        if bs.table.find('th', text='Recipe name'):
            tr = bs.table.find('tr')
            while tr:
                td = tr.find('td')
                tr = tr.findNext('tr')
                if not td:
                    continue
                qr = QueryResult()
                for f in ['recipe_name', 'version', 'description', 'layer']:
                    if f == 'recipe_name':
                        a = td.find('a')
                        if a:
                            setattr(qr, 'link', str(
                                "https://layers.openembedded.org"
                                + a.get('href', ''))
                            )
                    setattr(qr, f, str(td.text))
                    td = td.find_next_sibling()
                    if not td:
                        break
                if qr.link:
                    # Get first valid entry
                    self._query_url(qr.link)
                    return

    def _query_url(self, query_url):
        try:
            req = urllib.request.urlopen(query_url)
            read_str = req.read()
            bs = bs4.BeautifulSoup(read_str, "html.parser")
            th = bs.table.find('th', text='Name')
            while th:
                td = th.findNext('td')
                if td:
                    self._exists |= self._fill_field(
                        str(th.text), str(td.text))
                th = th.findNext('th')
        except Exception:
            self._exists = False
            return
        if not self._exists and bs:
            # Didn't match fully, so search on multi-match table
            self._get_first_on_multiple_matches(bs)
        else:
            # Confirm that the only recipe found is indeed in a valid layer
            for layer in self._prio_valid_layers:
                if self.layer.startswith(layer):
                    return
            self._exists = False

    def exists(self):
        return self._exists

    def query_recipe(self, recipe):
        if recipe:
            url_prefix = 'https://layers.openembedded.org/layerindex/branch/'
            url_prefix += '{}/recipes/'.format(self._oe_branch)
            url_prefix += '?q={}'
            for layer in self._prio_valid_layers:
                query_url = url_prefix.format(
                    recipe + urllib.parse.quote(' layer:') + layer)
                self._query_url(query_url)
                if self.exists():
                    return


def main():
    for recipe in [
        '', 'clang', 'ament_cmake_core', 'ament-cmake-core', 'libxml2',
            'bullet', 'sdl', 'sdl-image', 'qtbase']:
        print('Checking ' + recipe + '...')
        oe_query = OpenEmbeddedLayersDB()
        oe_query.query_recipe(recipe)
        if oe_query.exists():
            print(oe_query)
        else:
            print("Recipe {} doesn't exist!".format(recipe))
        print()


if __name__ == "__main__":
    main()
