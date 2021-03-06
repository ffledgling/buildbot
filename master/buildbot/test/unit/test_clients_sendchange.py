# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members


from twisted.trial import unittest
from twisted.internet import defer
from buildbot.clients import sendchange
from buildbot.test.util import pbclient

class Sender(unittest.TestCase, pbclient.PBClientMixin):

    def setUp(self):
        self.setUpPBClient()

        # results
        self.added_changes = []
        self.vc_used = None

    def _fake_callRemote(self, method, change):
        self.assertEqual(method, 'addChange')
        self.added_changes.append(change)
        return defer.succeed(None)

    def assertProcess(self, host, port, username, password, changes):
        self.assertEqual([host, port, username, password, changes],
                [ self.conn_host, self.conn_port,
                  self.creds.username, self.creds.password,
                  self.added_changes])

    def test_send_minimal(self):
        s = sendchange.Sender('localhost:1234')
        d = s.send('branch', 'rev', 'comm', ['a'])
        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project='', repository='', who=None, files=['a'],
                    comments='comm', branch='branch', revision='rev',
                    category=None, when=None, properties={}, revlink='',
                    src=None)])
        d.addCallback(check)
        return d

    def test_send_auth(self):
        s = sendchange.Sender('localhost:1234', auth=('me','sekrit'))
        d = s.send('branch', 'rev', 'comm', ['a'])
        def check(_):
            self.assertProcess('localhost', 1234, 'me', 'sekrit', [
                dict(project='', repository='', who=None, files=['a'],
                    comments='comm', branch='branch', revision='rev',
                    category=None, when=None, properties={}, revlink='',
                    src=None)])
        d.addCallback(check)
        return d

    def test_send_full(self):
        s = sendchange.Sender('localhost:1234')
        d = s.send('branch', 'rev', 'comm', ['a'], who='me', category='cats',
                   when=1234, properties={'a':'b'}, repository='r', vc='git',
                   project='p', revlink='rl')
        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project='p', repository='r', who='me', files=['a'],
                    comments='comm', branch='branch', revision='rev',
                    category='cats', when=1234, properties={'a':'b'},
                    revlink='rl', src='git')])
        d.addCallback(check)
        return d

    def test_send_files_tuple(self):
        # 'buildbot sendchange' sends files as a tuple, rather than a list..
        s = sendchange.Sender('localhost:1234')
        d = s.send('branch', 'rev', 'comm', ('a', 'b'))
        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project='', repository='', who=None, files=['a', 'b'],
                    comments='comm', branch='branch', revision='rev',
                    category=None, when=None, properties={}, revlink='',
                    src=None)])
        d.addCallback(check)
        return d

    def test_send_codebase(self):
        s = sendchange.Sender('localhost:1234')
        d = s.send('branch', 'rev', 'comm', ['a'], codebase='mycb')
        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project='', repository='', who=None, files=['a'],
                    comments='comm', branch='branch', revision='rev',
                    category=None, when=None, properties={}, revlink='',
                    src=None, codebase='mycb')])
        d.addCallback(check)
        return d

    def test_send_unicode(self):
        s = sendchange.Sender('localhost:1234')
        d = s.send(u'\N{DEGREE SIGN}',
                    u'\U0001f49e',
                    u'\N{POSTAL MARK FACE}',
                    [u'\U0001F4C1'],
                    project=u'\N{SKULL AND CROSSBONES}',
                    repository=u'\N{SNOWMAN}',
                    who=u'\N{THAI CHARACTER KHOMUT}',
                    category=u'\U0001F640',
                    when=1234,
                    properties={u'\N{LATIN SMALL LETTER A WITH MACRON}':'b'},
                    revlink=u'\U0001F517')

        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project=u'\N{SKULL AND CROSSBONES}',
                     repository=u'\N{SNOWMAN}',
                     who=u'\N{THAI CHARACTER KHOMUT}',
                     files=[u'\U0001F4C1'], # FILE FOLDER
                     comments=u'\N{POSTAL MARK FACE}',
                     branch=u'\N{DEGREE SIGN}',
                     revision=u'\U0001f49e', # REVOLVING HEARTS
                     category=u'\U0001F640', # WEARY CAT FACE
                     when=1234,
                     properties={u'\N{LATIN SMALL LETTER A WITH MACRON}':'b'},
                     revlink=u'\U0001F517', # LINK SYMBOL
                     src=None)])
        d.addCallback(check)
        return d

    def test_send_unicode_utf8(self):
        s = sendchange.Sender('localhost:1234')

        d = s.send(u'\N{DEGREE SIGN}'.encode('utf8'),
                u'\U0001f49e'.encode('utf8'),
                u'\N{POSTAL MARK FACE}'.encode('utf8'),
                [u'\U0001F4C1'.encode('utf8')],
                project=u'\N{SKULL AND CROSSBONES}'.encode('utf8'),
                repository=u'\N{SNOWMAN}'.encode('utf8'),
                who=u'\N{THAI CHARACTER KHOMUT}'.encode('utf8'),
                category=u'\U0001F640'.encode('utf8'),
                when=1234,
                properties={
                    u'\N{LATIN SMALL LETTER A WITH MACRON}'.encode('utf8')
                     : 'b'},
                revlink=u'\U0001F517'.encode('utf8'))

        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project=u'\N{SKULL AND CROSSBONES}',
                     repository=u'\N{SNOWMAN}',
                     who=u'\N{THAI CHARACTER KHOMUT}',
                     files=[u'\U0001F4C1'], # FILE FOLDER
                     comments=u'\N{POSTAL MARK FACE}',
                     branch=u'\N{DEGREE SIGN}',
                     revision=u'\U0001f49e', # REVOLVING HEARTS
                     category=u'\U0001F640', # WEARY CAT FACE
                     when=1234,
                     ## NOTE: not decoded!
                     properties={'\xc4\x81':'b'},
                     revlink=u'\U0001F517', # LINK SYMBOL
                     src=None)])
        d.addCallback(check)
        return d

    def test_send_unicode_latin1(self):
        # hand send() a bunch of latin1 strings, and expect them recoded
        # to unicode
        s = sendchange.Sender('localhost:1234', encoding='latin1')

        d = s.send(u'\N{YEN SIGN}'.encode('latin1'),
                u'\N{POUND SIGN}'.encode('latin1'),
                u'\N{BROKEN BAR}'.encode('latin1'),
                [u'\N{NOT SIGN}'.encode('latin1')],
                project=u'\N{DEGREE SIGN}'.encode('latin1'),
                repository=u'\N{SECTION SIGN}'.encode('latin1'),
                who=u'\N{MACRON}'.encode('latin1'),
                category=u'\N{PILCROW SIGN}'.encode('latin1'),
                when=1234,
                properties={
                    u'\N{SUPERSCRIPT ONE}'.encode('latin1')
                     : 'b'},
                revlink=u'\N{INVERTED QUESTION MARK}'.encode('latin1'))

        def check(_):
            self.assertProcess('localhost', 1234, 'change', 'changepw', [
                dict(project=u'\N{DEGREE SIGN}',
                     repository=u'\N{SECTION SIGN}',
                     who=u'\N{MACRON}',
                     files=[u'\N{NOT SIGN}'],
                     comments=u'\N{BROKEN BAR}',
                     branch=u'\N{YEN SIGN}',
                     revision=u'\N{POUND SIGN}',
                     category=u'\N{PILCROW SIGN}',
                     when=1234,
                     ## NOTE: not decoded!
                     properties={'\xb9':'b'},
                     revlink=u'\N{INVERTED QUESTION MARK}',
                     src=None)])
        d.addCallback(check)
        return d

