import random
from urllib.parse import urlencode

from locust import FastHttpUser, task
from scrapy.http.request.form import _get_form, _get_inputs


class BaseWagtailUser(FastHttpUser):
    abstract = True

    def on_start(self):
        # Login to the Wagtail admin so we can view the pages API
        response = self.client.get("/admin/login/")
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
        form_data_payload = urlencode(form_data).encode()
        self.client.post(
            "/admin/login/",
            data=form_data_payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            allow_redirects=False,
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
        # API always returns full URLs based on the Wagtail Site model - which by default has an
        # initial 127.0.0.1:8000 entry. Stripping this out for convenience if we're running this
        # remotely.
        page_url = wagtail_page["meta"]["html_url"]
        page_url = page_url.replace("http://127.0.0.1:8000", "")
        self.client.get(
            page_url,
            name="/[{}]".format(wagtail_page["meta"]["type"]),
        )


class WagtailEditor(BaseWagtailUser):
    fixed_count = 2

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
        form_data_payload = urlencode(form_data).encode()
        response = self.client.post(
            admin_url,
            name="/admin/pages/[{}]/edit/".format(wagtail_page["meta"]["type"]),
            data=form_data_payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            allow_redirects=False,
        )
