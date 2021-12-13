"""Unit tests for the member_management_list view"""

from django.test import TestCase
from clubs.models import User,Club,Role
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next


class MemberManagementListViewTestCase(TestCase,LogInTester):
    """Unit tests for the member management list."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_users.json',
    'clubs/tests/fixtures/other_clubs.json']


    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.url = reverse('member_management',kwargs={'club_name': self.club.club_name})

    def test_member_management_list_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/member_management/')

    def test_get_member_management_list_with_both_banned_and_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_members(15-1)
        self._create_test_banned_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_management.html')
        self.assertEqual(len(response.context['members']), 14)
        self.assertEqual(len(response.context['banned']), 14)
        self.assertFalse(response.context['member_is_empty'])
        self.assertFalse(response.context['banned_is_empty'])

    def test_get_member_management_list_with_no_banned_and_with_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_management.html')
        self.assertEqual(len(response.context['members']), 14)
        self.assertEqual(len(response.context['banned']), 0)
        self.assertFalse(response.context['member_is_empty'])
        self.assertTrue(response.context['banned_is_empty'])


    def test_get_member_management_list_with_banned_and_with_no_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_banned_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_management.html')
        self.assertEqual(len(response.context['members']), 0)
        self.assertEqual(len(response.context['banned']), 14)
        self.assertTrue(response.context['member_is_empty'])
        self.assertFalse(response.context['banned_is_empty'])

    def test_get_member_management_list_with_no_banned_and_no_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_management.html')
        self.assertEqual(len(response.context['members']), 0)
        self.assertEqual(len(response.context['banned']), 0)
        self.assertTrue(response.context['member_is_empty'])
        self.assertTrue(response.context['banned_is_empty'])

    def test_member_management_list_user_does_not_have_permission_is_member(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'MEM'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_member_management_list_does_not_have_permission_is_banned(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'BAN'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_member_management_list_user_does_not_have_permission_is_applicant(self):
        applicant = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(applicant,through_defaults={'club_role':'APP'})
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_member_management_list_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='janedoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_member_management_list_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in',self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_members(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                username=f'user{user_id}@test.org',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
            )
            self.club.club_members.add(user,through_defaults={'club_role':'MEM'})

    def _create_test_banned_members(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{20+user_id}',
                last_name=f'Last{20+user_id}',
                username=f'user{20+user_id}@test.org',
                password='Password123',
                bio=f'Bio {20+user_id}',
                chess_experience_level = 1,
            )
            self.club.club_members.add(user,through_defaults={'club_role':'BAN'})
