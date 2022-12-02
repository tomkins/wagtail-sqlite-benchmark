import random

from locust import HttpUser, task
from scrapy.http.request.form import _get_form, _get_inputs


class BaseWagtailUser(HttpUser):
    abstract = True

    def on_start(self):
        # Login to the Wagtail admin so we can view the pages API
        response = self.client.get("/admin/")
        form = _get_form(
            response,
            formname=None,
            formid=None,
            formnumber=0,
            formxpath=None,
        )
        form_data = _get_inputs(
            form,
            formdata={
                "username": "admin",
                "password": "changeme",
            },
            dont_click=False,
            clickdata=None,
        )
        self.client.post(
            "/admin/login/?next=/admin/",
            form_data,
        )

        # Store the list of pages for view_page
        pages_response = self.client.get("/admin/api/main/pages/")
        self.wagtail_pages = pages_response.json()["items"]


class WagtailUser(BaseWagtailUser):
    def on_start(self):
        super().on_start()

        # To avoid an admin session being used (with extra queries) - logout
        self.client.get("/admin/logout/")

    @task
    def view_page(self):
        wagtail_page = random.choice(self.wagtail_pages)
        self.client.get(
            wagtail_page["meta"]["html_url"],
            name="/[{}]".format(wagtail_page["meta"]["type"]),
        )


class WagtailEditor(BaseWagtailUser):
    fixed_count = 1

    @task
    def edit_page(self):
        wagtail_page = random.choice(self.wagtail_pages)
        admin_url = "/admin/pages/{}/edit/".format(wagtail_page["id"])
        response = self.client.get(
            admin_url,
            name="/admin/pages/[{}]/edit/".format(wagtail_page["meta"]["type"]),
        )
        form = _get_form(
            response,
            formname=None,
            formid="page-edit-form",
            formnumber=None,
            formxpath=None,
        )
        form_data = _get_inputs(
            form,
            formdata={
                "body-count": 0,
                "action-publish": "action-publish",
            },
            dont_click=False,
            clickdata=None,
        )
        response = self.client.post(
            admin_url,
            form_data,
            name="/admin/pages/[{}]/edit/".format(wagtail_page["meta"]["type"]),
        )
