"""Tests of the accept_applicant view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from .helpers import LogInTester,reverse_with_next


class AcceptApplicantViewTestCase(TestCase,LogInTester):
    """Tests of the accept_applicant view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.applicant = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.applicant,through_defaults={'club_role':'APP'})
        self.url = reverse('accept_applicant',kwargs={'club_name': self.club.club_name,'user_id':self.applicant.id})

    def test_accept_applicant_url(self):
        self.assertEqual(self.url,f'/applicants/{self.club.club_name}/accept/{self.applicant.id}/')

    def test_accept_applicant_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before = Role.objects.all().filter(club=self.club,club_role='APP').count()
        response = self.client.get(self.url)
        after =  Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before,after+1)
        role = self.applicant.role_set.get(club=self.club)
        self.assertEqual('MEM',role.club_role)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe@example.org")

    def test_accept_applicant_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before = Role.objects.all().filter(club=self.club,club_role='APP').count()
        url = reverse('accept_applicant', kwargs={'club_name':self.club.club_name,'user_id': self.applicant.id+9999})
        after = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before,after)
        role = self.applicant.role_set.get(club=self.club)
        self.assertEqual('APP',role.club_role)
        response = self.client.get(url, follow=True)
        response_url = reverse('applicants_list', kwargs={'club_name':self.club.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'applicants_list.html')

    def test_accept_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
