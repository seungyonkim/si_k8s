import os
import time
import yaml
from pydo import Client
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("DIGITALOCEAN_TOKEN")
client = Client(token=token)

req = {
    "name": "airflow-cluster",
    "region": "sfo2",
    "version": "1.28.2-do.0",
    "node_pools": [{"size": "s-1vcpu-2gb", "count": 2, "name": "worker-pool"}],
}

resp = client.kubernetes.create_cluster(body=req)

# Wait for the cluster to be provisioned
while True:
    print("Waiting for cluster to be provisioned...")
    cluster = client.kubernetes.get_cluster(resp["kubernetes_cluster"]["id"])
    if cluster["kubernetes_cluster"]["status"]["state"] == "running":
        break
    time.sleep(30)

# "68ca3765-a1fb-4981-b82c-be6cf92f4fb8"
# Get the kubeconfig
kubeconfig = client.kubernetes.get_kubeconfig(resp["kubernetes_cluster"]["id"])

# Load the existing kubeconfig
with open(os.path.expanduser("~/.kube/config"), "r") as f:
    existing_kubeconfig = yaml.safe_load(f)

# Load the new kubeconfig
new_kubeconfig = yaml.safe_load(kubeconfig)

# Merge the kubeconfigs
for context in new_kubeconfig["contexts"]:
    if context not in existing_kubeconfig["contexts"]:
        existing_kubeconfig["contexts"].append(context)

for cluster in new_kubeconfig["clusters"]:
    if cluster not in existing_kubeconfig["clusters"]:
        existing_kubeconfig["clusters"].append(cluster)

for user in new_kubeconfig["users"]:
    if user not in existing_kubeconfig["users"]:
        existing_kubeconfig["users"].append(user)

# Save the merged kubeconfig
with open(os.path.expanduser("~/.kube/config"), "w") as f:
    yaml.dump(existing_kubeconfig, f)
