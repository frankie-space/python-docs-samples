# Copyright 2016 Google Inc. All rights reserved.
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

# [START all]
import os

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
import jinja2
import webapp2


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)


class CounterHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {'counters': Counter.query()}
        counter_template = JINJA_ENV.get_template('counter.html')
        self.response.out.write(counter_template.render(template_values))

    def post(self):
        key = self.request.get('key')
        if key != '':
            # Add the task to the default queue.
            taskqueue.add(url='/worker', params={'key': key})
        self.redirect('/')


class CounterWorker(webapp2.RequestHandler):
    def post(self):  # should run at most 1/s due to entity group limit
        key = self.request.get('key')

        @ndb.transactional
        def update_counter():
            counter = Counter.get_or_insert(key, count=0)
            counter.count += 1
            counter.put()
        update_counter()


app = webapp2.WSGIApplication([
    ('/', CounterHandler),
    ('/worker', CounterWorker)
], debug=True)
# [END all]
