import pytest
import mock
import pwd
import grp
import subprocess
from collections import namedtuple
from lib.user_management import UserManagement


@mock.patch('pwd.getpwnam')
@pytest.mark.parametrize("login", [("elaine")])
def test_user_exist(mock_pwd, login):
    UserManagement.user_exist(login)
    pwd.getpwnam.assert_called_with('elaine')


@mock.patch('grp.getgrnam')
@pytest.mark.parametrize("github_team", [("soup")])
def test_group_exist(mock_grp, github_team):
    um = UserManagement()
    um.group_exist(github_team)
    grp.getgrnam.assert_called_with('soup')


@mock.patch('subprocess.run')
@mock.patch('os.mkdir')
@mock.patch('builtins.open')
@mock.patch('lib.user_management.UserManagement.add_ssh_pub_key')
@pytest.mark.parametrize("login, github_team, key", [("george", "soup", 'ssh-rsa key that is public')])
def test_add_user(mock_subprocess, mock_os, mock_open, mock_add_key, login, github_team, key):
    um = UserManagement()
    um.add_user(login, github_team, key)
    subprocess.run.assert_called_with(['useradd', '-m', '-G', 'soup', 'george'], check=True)
    um.add_ssh_pub_key.assert_called_with(login, key)


@mock.patch('subprocess.run')
@pytest.mark.parametrize("github_team", [("soup")])
def test_add_group(mock_subprocess, github_team):
    um = UserManagement()
    um.add_group(github_team)
    subprocess.run.assert_called_with(['groupadd', 'soup'], check=True)


@mock.patch('subprocess.run')
@mock.patch('os.mkdir')
@pytest.mark.parametrize("login", [("george")])
def test_purge_user(mock_subprocess, mock_os, login):
    um = UserManagement()
    um.purge_user(login)
    subprocess.run.assert_called_with(['userdel', '-r', 'george'], check=True)


@pytest.fixture
def create_pwd():
    data = []
    struct_passwd = namedtuple('struct_passwd', 'pw_name pw_passwd pw_uid pw_gid pw_gecos pw_dir pw_shell')
    data.append(struct_passwd(pw_name='root', pw_passwd='x', pw_uid=0, pw_gid=0, pw_gecos='root', pw_dir='/root', pw_shell='/bin/bash'))
    data.append(struct_passwd(pw_name='daemon', pw_passwd='x', pw_uid=1, pw_gid=1, pw_gecos='daemon', pw_dir='/usr/sbin', pw_shell='/usr/sbin/nologin'))
    data.append(struct_passwd(pw_name='soupnazi', pw_passwd='x', pw_uid=1000, pw_gid=1000, pw_gecos='soupnazi', pw_dir='/home/soup', pw_shell='/bin/bash'))
    data.append(struct_passwd(pw_name='elaine', pw_passwd='x', pw_uid=3001, pw_gid=3000, pw_gecos='elaine', pw_dir='/home/elaine', pw_shell='/bin/bash'))
    data.append(struct_passwd(pw_name='george', pw_passwd='x', pw_uid=3021, pw_gid=3000, pw_gecos='george', pw_dir='/home/george', pw_shell='/bin/bash'))
    return data


@mock.patch('pwd.getpwall')
@pytest.mark.parametrize("uid", [(999)])
def test_get_ids(our_pwd, uid):
    our_pwd.return_value = create_pwd()
    um = UserManagement()
    for id in um.get_ids(uid):
        assert id.pw_uid >= 1000


@mock.patch('pwd.getpwall')
@pytest.mark.parametrize("uid", [(0)])
def test_list_uids(our_pwd, uid):
    our_pwd.return_value = create_pwd()
    um = UserManagement()
    ids = []
    for id in um.get_ids(uid):
        ids.append(id.pw_uid)
    assert len(ids) == 5
    ids = []
    for id in um.get_ids(1000):
        ids.append(id.pw_uid)
    assert len(ids) == 3


@mock.patch('pwd.getpwall')
@pytest.mark.parametrize("uid", [(1000)])
def test_list_logins(our_pwd, uid):
    our_pwd.return_value = create_pwd()
    um = UserManagement()
    ids = []
    for id in um.get_ids(uid):
        ids.append(id.pw_name)
    assert ids == ['soupnazi', 'elaine', 'george']
