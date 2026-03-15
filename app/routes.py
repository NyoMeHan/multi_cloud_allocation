from flask import Blueprint, request, jsonify, Flask, render_template
from multi_cloud_allocation.app.optimizer.faker_data import FakeData
from flask_cors import CORS
from kubernetes import client, config
from multi_cloud_allocation.app.optimizer.optimizer import Optimizer

app = Flask(__name__)
bp = Blueprint('routes', __name__, template_folder='templates', static_folder='static')

CORS(bp, resources={r"/*": {"origins": "*"}})

optimizer = Optimizer()

@bp.route('/')
def home():
    return render_template('index.html')



@bp.route('/optimize/allocation/get_cpu_aws', methods=['GET']) #nmh
def get_cpu_aws():
    fake_data = FakeData()
    return jsonify(fake_data.get_aws_cpus())


@bp.route('/optimize/allocation/get_cpu_gcp', methods=['GET']) #nmh
def get_cpu_gcp():
    fake_data = FakeData()
    return jsonify(fake_data.get_gcp_cpus())



@bp.route('/optimize/allocation/get_aws_storage_type', methods=['GET']) #nmh
def get_aws_storage_type():
    fake_data = FakeData()
    return jsonify(fake_data.get_aws_storage_type())


@bp.route('/optimize/allocation/get_gcp_storage_type', methods=['GET']) #nmh
def get_gcp_storage_type():
    fake_data = FakeData()
    return jsonify(fake_data.get_gcp_storage_type())


@bp.route('/optimize/allocation/get_regions', methods=['GET']) #nmh
def get_regions():
    fake_data = FakeData()
    return jsonify(fake_data.get_regions())


@bp.route('/optimize/allocation/get_gcp_regions', methods=['GET']) #nmh
def get_gcp_regions():
    fake_data = FakeData()
    return jsonify(fake_data.get_gcp_regions())

@bp.route("/optimize/allocation/deploy_application", methods=["POST"]) #nmh
def deploy_application():
    data = request.get_json()
    print("Received data:", data)
    optimizer.deploy_application(data)
    return jsonify(
        optimizer.get_deployments()
    )


@bp.route('/optimize/allocation/get_deployments', methods=['GET']) #nmh
def get_deployment_data():
    return jsonify(optimizer.get_deployments())


@bp.route('/optimize/allocation/get_cluster_metrics', methods=['GET']) #nmh
def get_local_cluster_metrics():
    return jsonify(optimizer.get_local_clusters_metrics())

@bp.route('/optimize/allocation/get_aws_os_type', methods=['GET']) #nmh
def get_aws_os_type():
    fake_data = FakeData()
    return jsonify(fake_data.get_aws_os_types())



@bp.route('/optimize/allocation/get_gcp_os_type', methods=['GET']) #nmh
def get_gcp_os_type():
    fake_data = FakeData()
    return jsonify(fake_data.get_gcp_os_types())


@bp.route('/optimize/allocation/optimize_resources', methods=['POST']) #nmh
def optimize_resources():
    data = request.json
    namespace = data["namespace"]
    deployment = data["deployment"]
    new_cpu = data["cpu"]
    new_mem = data["memory"]
    data = request.get_json()
    print("Received data:", data)

    try:
        apps_v1 = client.AppsV1Api()

        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": deployment,
                            "resources": {
                                "requests": {"cpu": str(new_cpu), "memory": new_mem},
                                "limits": {"cpu": str(float(new_cpu) * 2), "memory": new_mem}
                            }
                        }]
                    }
                }
            }
        }

        apps_v1.patch_namespaced_deployment(name=deployment, namespace=namespace, body=patch)
        return jsonify({"status": f"Optimized resources for {deployment} in {namespace}."})

    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500


@bp.route('/optimize/allocation/get_pods_cpu_memory', methods=['GET']) #nmh
def get_pods_cpu_memory():
    return jsonify(optimizer.get_pods_cpu_memory())


@bp.route('/optimize/allocation/apply_suggestions', methods=['POST']) #nmh
def apply_suggestions():
    data = request.json
    selected = data.get("selected", [])

    applied_responses = []

    for item in selected:
        cluster = item["cluster"]
        suggestion = item["suggestion"]
        response = optimizer.apply_suggestion(cluster, suggestion)
        applied_responses.append(response)

    return jsonify({"status": "success", "applied": applied_responses})



@bp.route('/optimize/allocation/apply_cost_recommendations', methods=['POST']) #nmh
def apply_cost_recommendations():
    data = request.json
    selected = data.get("suggestions", [])
    cluster = data.get("cluster_name")
    applied_responses = []
    print("apply_cost_recommendations is called")
    print(data)

    for item in selected:
        suggestion = item
        response = optimizer.apply_cost_recommendations(cluster, suggestion)
        applied_responses.append(response)

    return jsonify({"status": "success", "applied": applied_responses})


