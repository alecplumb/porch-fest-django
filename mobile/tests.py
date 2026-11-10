from datetime                       import time

from django.contrib.auth.models     import User
from django.contrib.gis.geos        import Point
from django.test                    import TestCase

from performers.models              import Genre, Performer
from porches.models                 import Performance, Porch
from website.models                 import Sponsor

URL = "/api/mobile/v1/snapshot"


class SnapshotTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("organizer")

        cls.rock = Genre.objects.create(name="Rock", slug="rock")
        cls.folk = Genre.objects.create(name="Folk", slug="folk")

        cls.porch = Porch.objects.create(
            name="Blue Porch",
            number=7,
            owner_name="Private Owner",
            owner_email="owner@example.com",
            owner_phone="+15595550100",
            street_address="123 Olive Ave",
            city="Fresno",
            coordinates=Point(-119.805, 36.765),
            approved=True,
            porta_potty=True,
        )
        cls.unapproved = Porch.objects.create(
            name="Pending Porch",
            owner_name="Someone",
            owner_email="pending@example.com",
            street_address="1 Pending St",
            coordinates=Point(-119.8, 36.76),
            approved=False,
        )
        cls.unplaced = Porch.objects.create(
            name="No Pin Porch",
            owner_name="Someone",
            owner_email="nopin@example.com",
            street_address="2 Nowhere St",
            approved=True,
        )

        cls.band = Performer.objects.create(
            name="The Olives",
            slug="the-olives",     # explicit: Performer.save() can't generate one (missing slugify import upstream)
            bio="A band.",
            link="https://example.com/olives",
            email="band@example.com",
            phone_number="+15595550101",
        )
        cls.band.genres.set([cls.folk, cls.rock])
        cls.hidden_band = Performer.objects.create(name="Unscheduled", slug="unscheduled", email="hidden@example.com")

        cls.performance = Performance.objects.create(
            porch=cls.porch, performer=cls.band, created_by=user,
            start_time=time(13, 0), end_time=time(13, 45),
        )
        Performance.objects.create(
            porch=cls.unapproved, performer=cls.hidden_band, created_by=user,
            start_time=time(14, 0), end_time=time(14, 45),
        )

        Sponsor.objects.create(name="Tower Yoga", logo="sponsors/logos/yoga.jpg", porch=cls.porch, level=2)

    def test_shape(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()

        self.assertEqual(data["schema_version"], 1)
        self.assertEqual({g["slug"] for g in data["genres"]}, {"rock", "folk"})

        [porch] = data["porches"]
        self.assertEqual(porch["id"], str(self.porch.id))
        self.assertEqual(porch["slug"], "blue-porch")
        self.assertEqual(porch["number"], 7)
        self.assertEqual(porch["street_address"], "123 Olive Ave")
        self.assertAlmostEqual(porch["lat"], 36.765)
        self.assertAlmostEqual(porch["lng"], -119.805)
        self.assertTrue(porch["porta_potty"])
        self.assertIsNone(porch["image_url"])
        self.assertEqual(porch["sponsor"]["name"], "Tower Yoga")
        self.assertEqual(porch["sponsor"]["logo_url"], "http://testserver/media/sponsors/logos/yoga.jpg")

        [performer] = data["performers"]
        self.assertEqual(performer["id"], str(self.band.id))
        self.assertEqual(performer["genre_ids"], sorted([self.rock.id, self.folk.id]))

        [performance] = data["performances"]
        self.assertEqual(performance, {
            "id":           str(self.performance.id),
            "porch_id":     str(self.porch.id),
            "performer_id": str(self.band.id),
            "start_time":   "13:00:00",
            "end_time":     "13:45:00",
        })

    def test_private_contact_details_are_not_exposed(self):
        body = self.client.get(URL).content.decode()
        for secret in ("owner@example.com", "Private Owner", "5550100", "band@example.com", "5550101"):
            self.assertNotIn(secret, body)

    def test_unapproved_and_unplaced_porches_are_excluded(self):
        body = self.client.get(URL).content.decode()
        self.assertNotIn("Pending Porch", body)
        self.assertNotIn("No Pin Porch", body)
        self.assertNotIn("Unscheduled", body)

    def test_inactive_sponsor_is_omitted(self):
        Sponsor.objects.update(is_active=False)
        [porch] = self.client.get(URL).json()["porches"]
        self.assertIsNone(porch["sponsor"])

    def test_etag_round_trip(self):
        first = self.client.get(URL)
        etag = first["ETag"]
        self.assertTrue(etag.startswith('"'))

        cached = self.client.get(URL, headers={"If-None-Match": etag})
        self.assertEqual(cached.status_code, 304)
        self.assertEqual(cached.content, b"")
        self.assertEqual(cached["ETag"], etag)

        weak = self.client.get(URL, headers={"If-None-Match": f"W/{etag}"})
        self.assertEqual(weak.status_code, 304)

    def test_etag_changes_with_content(self):
        etag = self.client.get(URL)["ETag"]
        Performance.objects.filter(pk=self.performance.pk).update(start_time=time(15, 0))
        changed = self.client.get(URL, headers={"If-None-Match": etag})
        self.assertEqual(changed.status_code, 200)
        self.assertNotEqual(changed["ETag"], etag)

    def test_query_count_does_not_grow_with_rows(self):
        with self.assertNumQueries(5):
            self.client.get(URL)
