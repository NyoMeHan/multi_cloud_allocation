from datetime import datetime
import random
from faker import Faker


class FakeData:

    fake = Faker()

    cloud_providers = ["AWS", "GCP"]
    regions = {
        "AWS": ["us-east-1a", "eu-west-1b", "ap-south-1"],
        "GCP": ["us-central1-b", "asia-southeast1", "europe-west3"],
    }
    environments = ["dev", "staging", "prod"]
    apps = ["billing-api", "ml-model-server", "cart-service", "auth-service", "payment-api"]
    namespaces = ["billing-system", "ai-dev", "ecommerce-staging", "test-app", "payment-gateway"]


    def get_number_of_cpu(self):
        return [{"id":1, "text":"1 vCPU"}, {"id":2, "text":"2 vCPU"}, {"id":3, "text":"4 vCPU"}]

    def get_memory_size(self):
        arr = []
        for i in range(64):
            arr.append({"id":i, "text": str(i)})
        return arr

    def get_aws_storage_type(self):
        return [{"id":1, "text":"Gp2"},{"id":2, "text":"Gp3"},{"id":3, "text":"io1"},{"id":4, "text":"io2"},{"id":5, "text":"st1"},{"id":6, "text":"sc1"}, {"id":7, "text":"fsx"}]


    def get_gcp_storage_type(self):
        return [
          { "id": 1, "text": "pd-ssd" },
          { "id": 2, "text": "pd-ssd" },
          { "id": 3, "text": "pd-extreme" },
          { "id": 4, "text": "pd-extreme" },
          { "id": 5, "text": "pd-standard" },
          { "id": 6, "text": "pd-standard" },
          { "id": 7, "text": "pd-standard" }
        ]


    def get_regions(self):
        return [
          { "id": 1, "text": "us-east-1-N.Virginia" },
          { "id": 2, "text": "us-east-2-Ohio" },
          { "id": 3, "text": "us-west-1-N.California" },
          { "id": 4, "text": "us-west-2-Oregon" },
          { "id": 5, "text": "ca-central-1-CanadaCentral" },
          { "id": 6, "text": "sa-east-1-SaoPaulo" },
          { "id": 7, "text": "eu-west-1-Ireland" },
          { "id": 8, "text": "eu-west-2-London" },
          { "id": 9, "text": "eu-west-3-Paris" },
          { "id": 10, "text": "eu-central-1-Frankfurt" },
          { "id": 11, "text": "eu-north-1-Stockholm" },
          { "id": 12, "text": "eu-south-1-Milan" },
          { "id": 13, "text": "eu-south-2-Spain" },
          { "id": 14, "text": "ap-southeast-1-Singapore" },
          { "id": 15, "text": "ap-southeast-2-Sydney" },
          { "id": 16, "text": "ap-southeast-3-Jakarta" },
          { "id": 17, "text": "ap-northeast-1-Tokyo" },
          { "id": 18, "text": "ap-northeast-2-Seoul" },
          { "id": 19, "text": "ap-northeast-3-Osaka" },
          { "id": 20, "text": "ap-south-1-Mumbai" },
          { "id": 21, "text": "ap-south-2-Hyderabad" },
          { "id": 22, "text": "me-south-1-Bahrain" },
          { "id": 23, "text": "me-central-1-UAE" },
          { "id": 24, "text": "af-south-1-CapeTown" },
          { "id": 25, "text": "cn-north-1-Beijing" },
          { "id": 26, "text": "cn-northwest-1-Ningxia" }
        ]


    def get_gcp_regions(self):
        return [
          { "id": 1,  "text": "us-west1" },
          { "id": 2,  "text": "us-west2" },
          { "id": 3,  "text": "us-west3" },
          { "id": 4,  "text": "us-west4" },
          { "id": 5,  "text": "us-central1" },
          { "id": 6,  "text": "us-east1" },
          { "id": 7,  "text": "us-east4" },
          { "id": 8,  "text": "us-east5" },
          { "id": 9,  "text": "us-south1" },
          { "id": 10, "text": "northamerica-northeast1" },
          { "id": 11, "text": "northamerica-northeast2" },
          { "id": 12, "text": "northamerica-south1" },
          { "id": 13, "text": "southamerica-east1" },
          { "id": 14, "text": "southamerica-west1" },
          { "id": 15, "text": "europe-west1" },
          { "id": 16, "text": "europe-west2" },
          { "id": 17, "text": "europe-west3" },
          { "id": 18, "text": "europe-west4" },
          { "id": 19, "text": "europe-west6" },
          { "id": 20, "text": "europe-west8" },
          { "id": 21, "text": "europe-west9" },
          { "id": 22, "text": "europe-west10" },
          { "id": 23, "text": "europe-west12" },
          { "id": 24, "text": "europe-central2" },
          { "id": 25, "text": "europe-north1" },
          { "id": 26, "text": "europe-north2" },
          { "id": 27, "text": "europe-southwest1" },
          { "id": 28, "text": "me-west1" },
          { "id": 29, "text": "me-central1" },
          { "id": 30, "text": "me-central2" },
          { "id": 31, "text": "asia-south1" },
          { "id": 32, "text": "asia-south2" },
          { "id": 33, "text": "asia-southeast1" },
          { "id": 34, "text": "asia-southeast2" },
          { "id": 35, "text": "asia-east1" },
          { "id": 36, "text": "asia-east2" },
          { "id": 37, "text": "asia-northeast1" },
          { "id": 38, "text": "asia-northeast2" },
          { "id": 39, "text": "asia-northeast3" },
          { "id": 40, "text": "australia-southeast1" },
          { "id": 41, "text": "australia-southeast2" },
          { "id": 42, "text": "africa-south1" }
        ]


    def get_aws_os_types(self):
        return [
          { "id": 1, "text": "Debian-GNU-Linux" },
          { "id": 2, "text": "Ubuntu-LTS" },
          { "id": 3, "text": "Container-Optimized-OS-COS" },
          { "id": 4, "text": "Rocky-Linux" },
          { "id": 5, "text": "Red-Hat-Enterprise-Linux-RHEL" },
          { "id": 6, "text": "SUSE-Linux-Enterprise-Server-SLES" },
          { "id": 7, "text": "CentOS-deprecated" },
          { "id": 8, "text": "Windows-Server-2019" },
          { "id": 9, "text": "Windows-Server-2022" },
          { "id": 10, "text": "Google-Cloud-CLI-base-image-cloud-sdk" },
          { "id": 11, "text": "Fedora-CoreOS" },
          { "id": 12, "text": "Arch-Linux-community-maintained" }
        ]


    def get_gcp_os_types(self):

        return [
          { "id": 1, "text": "Debian" },
          { "id": 2, "text": "Ubuntu" },
          { "id": 3, "text": "CentOS" },
          { "id": 4, "text": "Red-Hat-Enterprise-Linux-RHEL" },
          { "id": 5, "text": "SUSE-Linux-Enterprise-Server-SLES" },
          { "id": 6, "text": "Rocky-Linux" },
          { "id": 7, "text": "AlmaLinux" },
          { "id": 8, "text": "Container-Optimized-OS-COS" },
          { "id": 9, "text": "Windows-Server" },
          { "id": 10, "text": "CoreOS-Fedora-CoreOS" },
          { "id": 11, "text": "Oracle-Linux" }
        ]



    def get_aws_cpus(self):
        return [
          { "id": 1, "text": "1 vCPU" },
          { "id": 2, "text": "2 vCPU" },
          { "id": 3, "text": "3 vCPU" },
          { "id": 4, "text": "4 vCPU" },
          { "id": 5, "text": "6 vCPU" },
          { "id": 6, "text": "8 vCPU" },
          { "id": 7, "text": "12 vCPU" },
          { "id": 8, "text": "16 vCPU" },
          { "id": 9, "text": "24 vCPU" },
          { "id": 10, "text": "32 vCPU" },
          { "id": 11, "text": "48 vCPU" },
          { "id": 12, "text": "64 vCPU" },
          { "id": 13, "text": "96 vCPU" }
        ]

    def get_gcp_cpus(self):
        return [
            {"id": 1, "text": "1 vCPU"},
            {"id": 2, "text": "2 vCPU"},
            {"id": 3, "text": "4 vCPU"},
            {"id": 4, "text": "8 vCPU"},
            {"id": 5, "text": "16 vCPU"},
            {"id": 6, "text": "24 vCPU"},
            {"id": 7, "text": "32 vCPU"},
            {"id": 8, "text": "48 vCPU"},
            {"id": 9, "text": "64 vCPU"},
            {"id": 10, "text": "72 vCPU"},
            {"id": 11, "text": "96 vCPU"},
            {"id": 12, "text": "128 vCPU"}
        ]


    def generate_fake_cluster_metrics(self):
        node_count = random.randint(3, 10)
        nodes = []

        for i in range(node_count):
            total_cpu = random.choice([2, 4, 8, 16])
            used_cpu = round(total_cpu * random.uniform(0.3, 0.9), 2)

            total_memory = random.choice([8, 16, 32, 64])  # in GiB
            used_memory = round(total_memory * random.uniform(0.3, 0.9), 2)

            nodes.append({
                "node_name": f"node-{i}",
                "cpu": {
                    "used": used_cpu,
                    "total": total_cpu,
                    "percentage": round((used_cpu / total_cpu) * 100, 2)
                },
                "memory": {
                    "used": used_memory,
                    "total": total_memory,
                    "percentage": round((used_memory / total_memory) * 100, 2)
                }
            })

        current_pods = random.randint(20, 50)
        desired_pods = current_pods + random.randint(-5, 10)

        resource_requests = {
            "cpu": round(random.uniform(0.5, 1.5), 2),  # in cores
            "memory": round(random.uniform(1.0, 4.0), 2)  # in GiB
        }

        resource_limits = {
            "cpu": resource_requests["cpu"] + random.uniform(0.5, 1.0),
            "memory": resource_requests["memory"] + random.uniform(1.0, 2.0)
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "cluster": {
                "total_nodes": node_count,
                "nodes": nodes
            },
            "pods": {
                "current": current_pods,
                "desired": desired_pods
            },
            "resource_settings": {
                "requests": resource_requests,
                "limits": {
                    "cpu": round(resource_limits["cpu"], 2),
                    "memory": round(resource_limits["memory"], 2)
                }
            }
        }
