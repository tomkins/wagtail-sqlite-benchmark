import random

from locust import HttpUser, task
from scrapy.http.request.form import _get_form, _get_inputs


class WagtailUser(HttpUser):
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

        # To avoid an admin session being used (with extra queries) - logout
        response = self.client.get("/admin/logout/")

    @task
    def view_page(self):
        wagtail_page = random.choice(self.wagtail_pages)
        self.client.get(
            wagtail_page["meta"]["html_url"],
            name="/[{}]".format(wagtail_page["meta"]["type"]),
        )
