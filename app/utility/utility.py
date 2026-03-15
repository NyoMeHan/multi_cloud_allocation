import re
import yaml


def generate_simulated_yaml(data, output_path="manifests/simulated.yaml"):
    cpu_millicores = data["cpu_number"]
    memory_gi = f"{data['memory_req']}Gi"
    storage_gi = f"{data['storage_size']}Gi"
    replicas = int(data["replica_count"])
    application_id = convert__valid_app_name(data['application_id'])

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{application_id}-deployment",
            "labels": {
                "app": application_id,
                "provider": data["cloud_provider"],
                "region": data["region"],
                "env": data["environment"],
                "os": data["os_type"]
            }
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": {
                    "app": application_id
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": application_id,
                        "env": data["environment"]
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": f"{application_id}-container",
                            "image": "nginx",  # or dynamic based on OS type
                            "resources": {
                                "requests": {
                                    "cpu": cpu_millicores,
                                    "memory": memory_gi
                                },
                                "limits": {
                                    "cpu": cpu_millicores,
                                    "memory": memory_gi
                                }
                            },
                            "env": [
                                {"name": "CLOUD_PROVIDER", "value": data["cloud_provider"]},
                                {"name": "CLOUD_REGION", "value": data["region"]},
                                {"name": "ENVIRONMENT", "value": data["environment"]},
                                {"name": "OS_TYPE", "value": data["os_type"]},
                                {"name": "STORAGE_TYPE", "value": data["storage_type"]}
                            ],
                            "volumeMounts": [
                                {
                                    "mountPath": "/data",
                                    "name": "storage-volume"
                                }
                            ]
                        }
                    ],
                    "volumes": [
                        {
                            "name": "storage-volume",
                            "emptyDir": {
                                "sizeLimit": storage_gi
                            }
                        }
                    ],
                    "nodeSelector": {
                        "cloud-provider": data["cloud_provider"]
                    }
                }
            }
        }
    }

    with open(output_path, "w") as f:
        yaml.dump(deployment, f)



def parse_cpu(cpu_str):
    match = re.match(r'(\d+)(m)?', cpu_str)
    if match:

        return int(match.group(1)) / 1000 if match.group(2) else int(match.group(1))
    else:
        return 0


def parse_memory(memory_str):
    match = re.match(r'(\d+)(Gi|Mi)?', memory_str)
    if match:

        if match.group(2) == 'Gi':
            return int(match.group(1))
        elif match.group(2) == 'Mi':
            return int(match.group(1)) / 1024
    return 0



def convert__valid_app_name(name):
    name = name.lower().strip()
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'[^a-z0-9.-]', '', name)
    name = re.sub(r'^[-.]+|[-.]+$', '', name)
    return name
