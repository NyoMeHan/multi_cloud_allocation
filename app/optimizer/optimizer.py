import re
import subprocess
from kubernetes import client, config
from kubernetes import config
from kubernetes.client.rest import ApiException
import random
from multi_cloud_allocation.app.utility import utility


class Optimizer:
    def deploy_application(self, data): #nmh
        utility.generate_simulated_yaml(data)

        if data["cloud_provider"] == 'aws':
            self.deploy_to_cluster("aws-cluster")
        else:
            self.deploy_to_cluster("gcp-cluster")


    def deploy_to_cluster(self, context_name):
        try:
            subprocess.run(["kubectl", "config", "use-context", context_name], check=True, capture_output=True,
                           text=True)
            subprocess.run(["kubectl", "apply", "-f", "manifests/simulated.yaml"], check=True, capture_output=True,
                           text=True)
        except subprocess.CalledProcessError as e:
            print(e.stderr or "No stderr output")
            return e.stderr or "No stderr output"



    def get_deployment_data(self):

        data = []

        kube_config = config.kube_config.load_kube_config()
        contexts = config.kube_config.list_kube_config_contexts(kube_config)[0]
        target_clusters = ['gcp-cluster', 'aws-cluster']
        target_contexts = [ctx for ctx in contexts if ctx['name'] in target_clusters]
        for ctx in target_contexts:
            context_name = ctx['name']
            print(f"Fetching deployments from cluster: {context_name}")

            config.load_kube_config(context=context_name)
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_deployment_for_all_namespaces().items

            for dep in deployments:
                info = self.get_deployment_data(dep)
                # Add cluster name to the info
                info['cluster'] = context_name
                print(info)
                if info.get('namespace') == "default":
                    data.append(info)
        data_recommendations = self.generate_cost_optimization_recommendations(data)
        return data_recommendations


    def get_monthly_cost(self, cpu_requested, memory_requested):
        #cpu_cost_per_hour = 0.03
        #memory_cost_per_hour = 0.01

        cpu_cost = utility.parse_cpu(cpu_requested)
        memory_cost = utility.parse_memory(memory_requested)

        return cpu_cost + memory_cost


    def get_deployments(self):

        data = []

        kube_config = config.kube_config.load_kube_config()
        contexts = config.kube_config.list_kube_config_contexts(kube_config)[0]
        target_clusters = ['gcp-cluster', 'aws-cluster']
        target_contexts = [ctx for ctx in contexts if ctx['name'] in target_clusters]
        for ctx in target_contexts:
            context_name = ctx['name']
            print(f"Fetching deployments from cluster: {context_name}")

            config.load_kube_config(context=context_name)
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_deployment_for_all_namespaces().items

            for dep in deployments:
                info = self.get_deployment_data(dep)
                # Add cluster name to the info
                info['cluster'] = context_name
                print(info)
                if info.get('namespace') == "default":
                    data.append(info)
        data_recommendations = self.generate_cost_optimization_recommendations(data)
        return data_recommendations


    def get_deployment_data(self, dep):

        metadata = dep.metadata
        labels = metadata.labels or {}
        containers = dep.spec.template.spec.containers
        container = containers[0] if containers else None

        env_vars = {env.name: env.value for env in container.env} if container and container.env else {}
        # environments = ["Production", "Staging", "Development", "Testing"]
        info = {
            "application": labels.get("app", metadata.name),
            "environment": labels.get("env", env_vars.get("ENVIRONMENT", "unknown")),
            "cluster": None,
            "namespace": metadata.namespace,
            "cloud_provider": labels.get("provider", env_vars.get("CLOUD_PROVIDER", "unknown")),
            "region": labels.get("region", env_vars.get("CLOUD_REGION", "unknown")),
            "cpu_requested": None,
            "memory_requested": None,
            "cpu_limit": None,
            "memory_limit": None,
            "monthly_cost": None,
            "replicas": dep.spec.replicas or 0
        }

        if container and container.resources:
            if container.resources.requests:
                info["cpu_requested"] = container.resources.requests.get("cpu")
                info["memory_requested"] = container.resources.requests.get("memory")
            if container.resources.limits:
                info["cpu_limit"] = container.resources.limits.get("cpu")
                info["memory_limit"] = container.resources.limits.get("memory")

        monthly_cost = self.get_monthly_cost(info["cpu_requested"], info["memory_requested"])
        info["monthly_cost"] = monthly_cost
        info["cluster"] = f"{info["environment"]}-cluster-{random.randint(100, 999)}",

        return info


    def get_local_clusters_metrics(self):
        cluster_metrics = {}

        interesting_clusters = ['gcp-cluster', 'aws-cluster']

        try:
            k_config = config.kube_config.load_kube_config()
            available_contexts = config.kube_config.list_kube_config_contexts(k_config)[0]
        except Exception as e:
            print(f"Ugh, config loading failed again: {e}")
            return None

        # Loop through contexts and get metrics
        for context in available_contexts:
            cluster_name = context['name']

            if cluster_name not in interesting_clusters:
                continue

            print(f"Getting metrics from {cluster_name}...")

            config.load_kube_config(context=cluster_name)
            core_api = client.CoreV1Api()
            custom_api = client.CustomObjectsApi()  # for metrics
            apps_api = client.AppsV1Api()  # for deployments

            node_metrics = []

            # Get info about each node
            for node in core_api.list_node().items:
                node_name = node.metadata.name
                resources = node.status.allocatable

                # Calculate CPU cores
                if 'm' in resources.get('cpu', '0'):
                    total_cores = int(float(resources.get('cpu', '0').replace('m', '')) / 1000)
                else:
                    total_cores = int(resources.get('cpu', '0'))

                # Memory in GiB
                mem_str = resources.get('memory', '0')
                total_mem = int(mem_str.replace('Ki', '').replace('Mi', '000').replace('Gi', '000000')) / 1048576

                # get actual usage metrics
                try:
                    metrics_response = custom_api.list_cluster_custom_object(
                        group="metrics.k8s.io",
                        version="v1beta1",
                        plural="nodes"
                    )

                    # Find matching metrics for this node
                    for metric in metrics_response['items']:
                        if metric['metadata']['name'] == node_name:

                            cpu_usage = metric['usage']['cpu']
                            if 'm' in cpu_usage:
                                used_cpu = int(cpu_usage.replace('m', '')) / 1000
                            elif 'n' in cpu_usage:  # sometimes we get nano-cores ¯\_(ツ)_/¯
                                used_cpu = int(cpu_usage.replace('n', '')) / 1_000_000_000
                            else:
                                used_cpu = float(cpu_usage)

                            mem_usage = metric['usage']['memory']
                            used_mem = int(
                                mem_usage.replace('Ki', '').replace('Mi', '000').replace('Gi', '000000')) / 1048576

                            cpu_pct = (used_cpu / total_cores * 100) if total_cores else 0
                            mem_pct = (used_mem / total_mem * 100) if total_mem else 0

                            node_metrics.append({
                                "node_name": node_name,
                                "cpu": {
                                    "percentage": round(cpu_pct, 2),
                                    "total": total_cores,
                                    "used": round(used_cpu, 2)
                                },
                                "memory": {
                                    "percentage": round(mem_pct, 2),
                                    "total": round(total_mem, 2),
                                    "used": round(used_mem, 2)
                                }
                            })
                            break

                except ApiException as e:
                    print(f"Failed to get metrics for {node_name} :( Error: {e}")

                    node_metrics.append({
                        "node_name": node_name,
                        "cpu": {"percentage": 0, "total": total_cores, "used": 0},
                        "memory": {"percentage": 0, "total": round(total_mem, 2), "used": 0}
                    })

            # Get pod metrics only for deployments
            pods = [p for p in core_api.list_pod_for_all_namespaces().items
                    if p.metadata.namespace != 'kube-system']

            # Calculate total resource requests
            total_cpu = 0
            total_mem = 0
            for pod in pods:
                for container in pod.spec.containers:
                    if container.resources.requests:
                        cpu_req = container.resources.requests.get('cpu', '0')
                        if 'm' in cpu_req:
                            total_cpu += float(cpu_req.replace('m', '')) / 1000
                        else:
                            total_cpu += float(cpu_req)

                        mem_req = container.resources.requests.get('memory', '0')
                        total_mem += int(
                            mem_req.replace('Ki', '').replace('Mi', '000').replace('Gi', '000000')) / 1048576

            # Get pod count from deployments
            user_deployments = [d for d in apps_api.list_deployment_for_all_namespaces().items
                                if d.metadata.namespace != 'kube-system']
            pod_count = sum(d.spec.replicas for d in user_deployments if d.spec.replicas) or len(pods)

            cluster_metrics[cluster_name] = {
                "nodes": node_metrics,
                "aggregate": {
                    "cpu_limit": round(total_cpu, 2),
                    "pod_count": pod_count,
                    "memory_limit": round(total_mem / 1024, 2)  # Convert to GiB
                }
            }

        # Get recommendations based on metrics
        return self.get_recommendations_resource(cluster_metrics)


    # Get total resource usage from clusters
    def get_pods_cpu_memory(self):
        # Get all contexts
        contexts, current_ctx = config.kube_config.list_kube_config_contexts()

        # keep only aws-cluster and gcp-cluster, exclude otther contexts
        skip_namespaces = {"kube-system", "kube-public", "kube-node-lease", "local-path-storage"}

        cpu_req_sum = 0
        cpu_lim_sum = 0
        mem_req_sum = 0
        mem_lim_sum = 0
        pods_desired_total = 0
        pods_running_total = 0

        for ctx_info in contexts:
            ctx_name = ctx_info['name']

            if ctx_name not in ["aws-cluster", "gcp-cluster"]:
                continue

            print(f"--> Getting resources for cluster: {ctx_name}")
            config.load_kube_config(context=ctx_name)

            apps_api = client.AppsV1Api()
            core_api = client.CoreV1Api()

            # Figure out which namespaces are "ours"
            all_ns_objs = core_api.list_namespace().items
            user_ns_list = [ns.metadata.name for ns in all_ns_objs if ns.metadata.name not in skip_namespaces]

            # calculate totals for just current cluster
            cluster_cpu_req = 0
            cluster_cpu_lim = 0
            cluster_mem_req = 0
            cluster_mem_lim = 0
            desired_pods = 0
            running_pods = 0

            for namespace in user_ns_list:
                try:
                    deployments = apps_api.list_namespaced_deployment(namespace=namespace).items
                except Exception as e:
                    print(f"Skipping namespace {namespace} due to error: {e}")
                    continue

                for dep in deployments:
                    for c in dep.spec.template.spec.containers:
                        res = c.resources

                        if res and res.requests:
                            cpu_str = res.requests.get("cpu", "0")
                            mem_str = res.requests.get("memory", "0")
                            cluster_cpu_req += utility.parse_cpu(cpu_str)
                            cluster_mem_req += utility.parse_memory(mem_str)

                        if res and res.limits:
                            cpu_lim_str = res.limits.get("cpu", "0")
                            mem_lim_str = res.limits.get("memory", "0")
                            cluster_cpu_lim += utility.parse_cpu(cpu_lim_str)
                            cluster_mem_lim += utility.parse_memory(mem_lim_str)

                    desired_pods += dep.spec.replicas or 0
                    running_pods += dep.status.replicas or 0

            # Accumulate all clusters
            cpu_req_sum += cluster_cpu_req
            cpu_lim_sum += cluster_cpu_lim
            mem_req_sum += cluster_mem_req
            mem_lim_sum += cluster_mem_lim
            pods_desired_total += desired_pods
            pods_running_total += running_pods

        results = {
            "cpu_request": round(cpu_req_sum, 2),  # rounding just for display purposes
            "cpu_limit": round(cpu_lim_sum, 2),
            "memory_request": round(mem_req_sum, 2),
            "memory_limit": round(mem_lim_sum, 2),
            "desired_pod_count": pods_desired_total,
            "current_pod_count": pods_running_total
        }

        return results



    def get_recommendations_resource(self, all_metrics):

        for cluster_name, metrics in all_metrics.items():
            suggestions = []

            for node in metrics['nodes']:
                if node["cpu"]["percentage"] >= 80:
                    suggestions.append(
                        f"Scale up CPU on node {node['node_name']} (CPU usage: {node['cpu']['percentage']}%)")
                elif node["cpu"]["percentage"] < 75:
                    suggestions.append(
                        f"Scale down CPU on node {node['node_name']} (CPU usage: {node['cpu']['percentage']}%)")

                if node["memory"]["percentage"] < 40:
                    suggestions.append(
                        f"Scale down Memory on node {node['node_name']} (Memory usage: {node['memory']['percentage']}%)")
                elif node["memory"]["percentage"] >= 50:
                    suggestions.append(
                        f"Scale up Memory on node {node['node_name']} (Memory usage: {node['memory']['percentage']}%)")

            # Cluster-level suggestions
            cpu_limit = metrics['aggregate']['cpu_limit']
            memory_limit = metrics['aggregate']['memory_limit']

            if cpu_limit > 0:
                cluster_cpu_percentage = sum(n["cpu"]["used"] for n in metrics['nodes']) / cpu_limit * 100
                if cluster_cpu_percentage >= 75:
                    suggestions.append(
                        f"Scale up pods (CPU usage: {round(cluster_cpu_percentage, 2)}%) - Consider increasing pod replicas or node capacity.")
                elif cluster_cpu_percentage < 75:
                    suggestions.append(
                        f"Scale down pods (CPU usage: {round(cluster_cpu_percentage, 2)}%) - Consider reducing pod replicas.")

            if memory_limit > 0:
                cluster_memory_percentage = sum(n["memory"]["used"] for n in metrics['nodes']) / (
                        memory_limit / 1024) * 100
                if cluster_memory_percentage < 50:
                    suggestions.append(
                        f"Scale down pods (Memory usage: {round(cluster_memory_percentage, 2)}%) - Consider reducing pod replicas.")
                elif cluster_memory_percentage >= 50:
                    suggestions.append(
                        f"Scale up pods (Memory usage: {round(cluster_memory_percentage, 2)}%) - Consider increasing pod replicas or memory requests.")
            metrics["suggestions"] = suggestions


        return all_metrics



    def patch_pod_resources(self, cpu=None, memory=None, namespace="default"):
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()

        try:
            deployments = apps_v1.list_namespaced_deployment(namespace)
        except ApiException as e:
            print(f"Failed to list deployments: {e}")
            return

        for dep in deployments.items:
            name = dep.metadata.name

            try:
                latest_dep = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            except ApiException as e:
                print(f"Failed to read deployment {name}: {e}")
                continue

            containers_patch = []
            for container in latest_dep.spec.template.spec.containers:
                container_patch = {
                    "name": container.name,
                    "resources": {
                        "requests": {},
                        "limits": {}
                    }
                }
                if cpu:
                    container_patch["resources"]["requests"]["cpu"] = cpu
                    container_patch["resources"]["limits"]["cpu"] = cpu
                if memory:
                    container_patch["resources"]["requests"]["memory"] = memory
                    container_patch["resources"]["limits"]["memory"] = memory

                containers_patch.append(container_patch)

            patch_body = {
                "spec": {
                    "template": {
                        "spec": {
                            "containers": containers_patch
                        }
                    }
                }
            }

            try:
                apps_v1.patch_namespaced_deployment(
                    name=name,
                    namespace=namespace,
                    body=patch_body
                )
                print(f"Updated resources for {name}")
            except ApiException as e:
                print(f"Failed to patch {name}: {e.reason} - {e.body}")



    def apply_suggestion(self, cluster_name, suggestion_text):
        config.load_kube_config(context=cluster_name)
        namespace = "default"
        apps_v1 = client.AppsV1Api()

        if "Scale down pods" in suggestion_text and "reducing pod replicas" in suggestion_text:
            deployments = apps_v1.list_namespaced_deployment(namespace)
            for dep in deployments.items:
                current_replicas = dep.spec.replicas
                if current_replicas and current_replicas > 1:
                    new_replicas = current_replicas - 1

                    patch_body = {
                        "spec": {
                            "replicas": new_replicas
                        }
                    }

                    apps_v1.patch_namespaced_deployment(
                        name=dep.metadata.name,
                        namespace=namespace,
                        body=patch_body
                    )
                    print(f"Scaled down {dep.metadata.name} to {new_replicas} replicas")

        elif "Scale up pods" in suggestion_text and "increasing pod replicas" in suggestion_text:
            deployments = apps_v1.list_namespaced_deployment(namespace)
            for dep in deployments.items:
                current_replicas = dep.spec.replicas or 1
                new_replicas = current_replicas + 1

                patch_body = {
                    "spec": {
                        "replicas": new_replicas
                    }
                }

                apps_v1.patch_namespaced_deployment(
                    name=dep.metadata.name,
                    namespace=namespace,
                    body=patch_body
                )
                print(f"Scaled up {dep.metadata.name} to {new_replicas} replicas")

        elif "Scale down CPU" in suggestion_text:
            self.patch_pod_resources(cpu="250m", namespace=namespace)

        elif "Scale up CPU" in suggestion_text:
            self.patch_pod_resources(cpu="500m", namespace=namespace)

        elif "Scale down Memory" in suggestion_text:
            self.patch_pod_resources(memory="256Mi", namespace=namespace)

        elif "Scale up Memory" in suggestion_text:
            self.patch_pod_resources(memory="512Mi", namespace=namespace)



    # Fetches pod-level CPU and memory usage for a specific app
    def get_pod_usage(self, namespace, app_name):
        # Load kube config
        config.load_kube_config()

        metrics_api = client.CustomObjectsApi()

        total_cpu = 0
        total_mem = 0
        pod_counter = 0

        try:
            # get metrics from the metrics server
            metrics_response = metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )

            pods = metrics_response.get('items', [])

            for pod in pods:
                pod_meta = pod.get('metadata', {})
                pod_labels = pod_meta.get('labels', {})

                if pod_labels.get("app") != app_name:
                    continue  # Not our pod, skip

                container_data = pod.get('containers', [])
                for container in container_data:
                    usage_data = container.get('usage', {})
                    cpu_raw = usage_data.get('cpu', '0')
                    mem_raw = usage_data.get('memory', '0')
                    parsed_cpu = utility.parse_cpu(cpu_raw)
                    parsed_mem = utility.parse_memory(mem_raw)
                    total_cpu += parsed_cpu
                    total_mem += parsed_mem
                    pod_counter += 1

            return total_cpu, total_mem, pod_counter

        except ApiException as err:
            print(f"Error fetching metrics for app '{app_name}' in namespace '{namespace}': {err}")
            return 0, 0, 0  # Default to 0s if things blow up



    def generate_cost_optimization_recommendations(self, app_data):
        # fake pricing model for CPU and memory
        cpu_price = 1.0
        mem_price = 0.1

        # Collect apps by cluster
        apps_by_cluster = {}
        for entry in app_data:
            clus = entry['cluster']
            if clus not in apps_by_cluster:
                apps_by_cluster[clus] = []
            apps_by_cluster[clus].append(entry)

        for entry in app_data:
            app_name = entry['application']
            ns = entry['namespace']
            tips = []

            # Convert resource strings to numeric values
            cpu_req = utility.parse_cpu(entry['cpu_requested'])
            cpu_lim = utility.parse_cpu(entry['cpu_limit'])
            mem_req = utility.parse_memory(entry['memory_requested'])
            mem_lim = utility.parse_memory(entry['memory_limit'])

            # Fetch average usage per pod
            used_cpu, used_mem, pod_cnt = self.get_pod_usage(ns, app_name)

            if pod_cnt > 0:
                used_cpu = used_cpu / pod_cnt
                used_mem = used_mem / pod_cnt

            entry['cpu_used'] = round(used_cpu, 3)
            entry['memory_used'] = round(used_mem, 3)

            # Ratios of requested vs actually used
            cpu_ratio = used_cpu / cpu_req if cpu_req > 0 else 1  # avoid div-by-zero
            mem_ratio = used_mem / mem_req if mem_req > 0 else 1
            cpu_overalloc = cpu_lim / cpu_req if cpu_req > 0 else 1
            mem_overalloc = mem_lim / mem_req if mem_req > 0 else 1

            # CPU is over-provisioned compared to actual usage
            if cpu_ratio < 0.5 and cpu_req > 0.1:
                suggested_cpu = max(0.1, used_cpu * 1.2)
                cpu_savings = (cpu_req - suggested_cpu) * cpu_price
                tips.append(
                    f"Lower CPU request from {cpu_req:.2f} to {suggested_cpu:.2f} cores – potential monthly savings: ${cpu_savings:.2f}")

            # Memory over provision
            if mem_ratio < 0.5 and mem_req > 0.5:
                suggested_mem = max(0.5, used_mem * 1.2)
                mem_savings = (mem_req - suggested_mem) * mem_price
                tips.append(
                    f"Memory request is high. Consider reducing from {mem_req:.2f} GiB to {suggested_mem:.2f} GiB to save ${mem_savings:.2f}/month")

            # CPU limits too high
            if cpu_overalloc > 1.5:
                better_cpu_lim = cpu_req * 1.1  # leaving a bit of headroom
                lim_savings = (cpu_lim - better_cpu_lim) * cpu_price * 0.5  # less impact than request changes
                tips.append(
                    f"Too much headroom in CPU limit. Maybe drop from {cpu_lim:.2f} to {better_cpu_lim:.2f} cores for a soft saving of ${lim_savings:.2f}")

            if mem_overalloc > 1.5:
                better_mem_lim = mem_req * 1.1
                lim_mem_savings = (mem_lim - better_mem_lim) * mem_price * 0.5
                tips.append(
                    f"Memory limit might be overkill. Try reducing from {mem_lim:.2f} GiB to {better_mem_lim:.2f} GiB – est. savings: ${lim_mem_savings:.2f}")

            # Monthly cost
            if entry['monthly_cost'] > 10:
                tips.append(
                    f"{app_name} has a relatively high monthly cost (${entry['monthly_cost']:.2f}). Might be worth deeper analysis or combining with other apps.")

            low_cost_buddies = [
                app for app in apps_by_cluster[entry['cluster']]
                if app['monthly_cost'] < 1 and utility.parse_cpu(app['cpu_requested']) < 0.5
            ]
            if len(low_cost_buddies) > 2:
                tips.append(
                    f"Notice: Cluster {entry['cluster']} has several tiny-cost apps – maybe bundle them to simplify overhead.")

            if not tips:
                tips.append(f"{app_name} looks good – using resources efficiently at ${entry['monthly_cost']:.2f}/month.")

            entry['recommendations'] = tips

        return app_data


    def apply_cost_recommendations(self, cluster_name, suggestion_text):
        print(f"[DEBUG] Starting cost recommendations for cluster: {cluster_name} — Suggestion: '{suggestion_text}'")

        try:
            # Set context for kubectl
            config.load_kube_config(context=cluster_name)

            namespace = "default"
            apps_v1 = client.AppsV1Api()
            target_app = "airticket-booking-system-front-end"  # NOTE: hardcoded for now, may need to generalize

            # CPU suggestion
            cpu_match = re.search(r'(Reduce|Increase) CPU request from [\d\.]+ to ([\d\.]+) cores', suggestion_text)
            print(f"Parsed CPU match: {cpu_match}")

            if cpu_match:
                new_cpu_val = float(cpu_match.group(2))
                # Converting to 'millicore'
                cpu_str = str(int(new_cpu_val * 1000)) + "m"
                self.patch_deployment_resources_by_name(apps_v1, target_app, namespace, cpu=cpu_str)

            # Memory suggestion
            mem_match = re.search(r'(Reduce|Increase) memory request from [\d\.]+ GiB to ([\d\.]+) GiB',
                                  suggestion_text)
            print(f"Parsed Memory match: {mem_match}")

            if mem_match:
                mem_gib = float(mem_match.group(2))
                # Converting GiB to MiB
                mem_str = str(int(mem_gib * 1024)) + "Mi"
                self.patch_deployment_resources_by_name(apps_v1, target_app, namespace, memory=mem_str)

            if "scale down pods" in suggestion_text.lower() or "reducing pod replicas" in suggestion_text.lower():
                deployment_list = apps_v1.list_namespaced_deployment(namespace)
                for dep in deployment_list.items:
                    if dep.metadata.name == target_app:
                        curr_replicas = dep.spec.replicas or 1
                        if curr_replicas > 1:
                            updated_replicas = curr_replicas - 1
                            self.patch_deployment_replicas(apps_v1, dep.metadata.name, namespace, updated_replicas)


            if "scale up pods" in suggestion_text.lower() or "increasing pod replicas" in suggestion_text.lower():
                deployments = apps_v1.list_namespaced_deployment(namespace)
                for dep in deployments.items:
                    if dep.metadata.name == target_app:
                        existing_replicas = dep.spec.replicas or 1
                        self.patch_deployment_replicas(apps_v1, dep.metadata.name, namespace, existing_replicas + 1)

            return {
                "success": True,
                "message": "Suggestion applied successfully"
            }

        except Exception as err:
            print(f"[ERROR] Something went wrong: {err}")
            return {
                "success": False,
                "message": f"Error: {str(err)}"
            }



    def patch_deployment_resources_by_name(self, apps_v1, dep_name, namespace, cpu=None, memory=None):
        print(f"Attempting to patch deployment: '{dep_name}' in namespace '{namespace}'")

        try:
            # get the deployments
            deployment_obj = apps_v1.read_namespaced_deployment(dep_name, namespace)
        except client.exceptions.ApiException as ex:
            print(f"Error: Could not find deployment '{dep_name}'. Details: {ex}")
            return

        container_list = deployment_obj.spec.template.spec.containers
        if not container_list:
            print(f"Warning: No containers found in deployment '{dep_name}' — nothing to update.")
            return


        target_container = container_list[0].name

        # Building the patch payload
        patch_payload = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": target_container,
                                "resources": {
                                    "requests": {}
                                }
                            }
                        ]
                    }
                }
            }
        }

        # Only include the resources to update
        if cpu:
            patch_payload["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"] = cpu
        if memory:
            patch_payload["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["memory"] = memory

        try:
            result = apps_v1.patch_namespaced_deployment(
                name=dep_name,
                namespace=namespace,
                body=patch_payload
            )
            print(
                f"Success: Patched deployment '{dep_name}' — CPU: {cpu or 'unchanged'}, Memory: {memory or 'unchanged'}")

            return {f"Success: Patched deployment '{dep_name}' — CPU: {cpu or 'unchanged'}, Memory: {memory or 'unchanged'}"}
        except Exception as patch_err:
            print(f"Error while patching '{dep_name}': {patch_err}")
            return {f"Error while patching '{dep_name}': {patch_err}"}



    def patch_deployment_replicas(self, apps_v1, deployment_name, namespace, new_replicas):
        patch_body = {
            "spec": {
                "replicas": new_replicas
            }
        }
        apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch_body
        )
        print(f"Scaled {deployment_name} to {new_replicas} replicas")