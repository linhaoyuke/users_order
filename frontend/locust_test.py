import os

from locust import HttpUser, TaskSet, task, between


class LoginTaskSet(TaskSet):
    @task
    def get_login_page_with_assets(self):
        """
        Task to simulate a user visiting the login page and downloading its main assets.
        """
        # Step 1: Request the main HTML page.
        # We use 'name' to group similar requests in the statistics.
        self.client.get("/login", name="/login-page")

        # Step 2: Add requests for large static assets to simulate network traffic.
        # Confirmed background image path from Login.vue is /1.jpeg
        self.client.get("/1.jpeg", name="/static-assets")
        self.client.get("/src/main.ts", name="/static-assets")
        self.client.get("/@vite/client", name="/static-assets")


class WebsiteUser(HttpUser):
    tasks = [LoginTaskSet]

    # Now that each task simulates a more complete page load, having a "think time"
    # between requests is important for realistic simulation.
    wait_time = between(1.5, 5)

    def on_start(self):
        print("A new user is starting.")
        self.client.verify = False
        self.client.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }


if __name__ == "__main__":
    os.system("locust -f locust_test.py --host=http://47.121.117.190:9090")
