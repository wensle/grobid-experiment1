import docker
from docker.models.containers import Container
from docker.models.images import Image
from docker import DockerClient


class GrobidContainer:
    name = "grobid/grobid"
    tag = "0.7.3"

    def __init__(self):
        self.client: DockerClient = docker.from_env()

    @property
    def repo_tags(self):
        return f"{self.name}:{self.tag}"

    def remove(self):
        container: Container
        for container in self.client.containers.list():
            image: Image = container.image
            if self.repo_tags in image.attrs["RepoTags"]:
                container.kill()
                container.wait(condition="removed")

    def run(self):
        gpu_request = docker.types.DeviceRequest(
            count=-1,
            capabilities=[["gpu"]],
        )

        if self.is_running():
            return

        self.client.containers.run(
            image=self.repo_tags,
            detach=True,
            ports={"8070/tcp": 8070},
            device_requests=[gpu_request],
            remove=True,
        )

    def is_running(self):
        container: Container
        for container in self.client.containers.list():
            image: Image = container.image
            if (
                self.repo_tags in image.attrs["RepoTags"]
                and container.status == "running"
            ):
                return True

        return False
