# Installing Kubernetes
The official guide for install Kubernetes can be found [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/). However we will be following the guide from [k8s-on-raspbian](https://github.com/teamserverless/k8s-on-raspbian/blob/master/GUIDE.md). Note that there is exists a light weight version on kubernetes called [K3s](https://blog.alexellis.io/raspberry-pi-homelab-with-k3sup/) and an alternative to Raspbian called [HypriotOS](https://blog.hypriot.com/post/setup-kubernetes-raspberry-pi-cluster/) which is optmized for Docker.

1. Install Docker
```
curl -sSL get.docker.com | sh
sudo usermod pi -aG docker && newgrp docker
```
2. Disable Swap
```
sudo dphys-swapfile swapoff && \
sudo dphys-swapfile uninstall && \
sudo update-rc.d dphys-swapfile remove && \
sudo systemctl disable dphys-swapfile
```
3. Enable cgroup memory
```
sudo echo "$(head -n1 /boot/cmdline.txt) cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory" > /boot/cmdline.txt
```
This removes the newline and adds `cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory` to the bootfile `/boot/cmdline.txt`, alternatively use:
```
sudo sed -i '$ s/$/ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory/' /boot/cmdline.txt
```
4. Reboot Computer
```
sudo shutdown -r now
```
5. Install Kubernetes Administration tool kubeadm
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - && \
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list && \
sudo apt-get update -q && \
sudo apt-get install -qy kubeadm && \
sudo systemctl enable kubelet
```
Note: Steps 6-11 are for the Master Node only. Step 12 is for the Worker Node only. All other steps must run on all the nodes of the cluster.

6. Pull pre-requisites Docker images 
```
sudo kubeadm config images pull -v3
```
7. Initialize master node
```
sudo kubeadm init --token-ttl=0
```
8. Run the printed code
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
9. Set-up pod network (Weave Net)
```
kubectl apply -f \
"https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
```

11. Print the Join token
```
kubeadm token create --print-join-command
```

12. Join the Master node
```
kubeadm join --token <token> <master-ip> --discovery-token-ca-cert-hash <hash>
```

10. Set up ip-tables
```
sudo sysctl net.bridge.bridge-nf-call-iptables=1
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy 
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy 
```

Now we are done, on the master node we can check that that all nodes are connected
```
kubectl get nodes
```
# Start up the Kubernetes dashboard
1. Create the dashboard pods and services
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/aio/deploy/recommended.yaml
```

2. Create a dashboard account
```
kubectl create serviceaccount dashboard-admin
```

3. Set the account persissions
```
kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=default:dashboard-admin
```
4. Copy the name of the token
```
$ kubectl get secrets
NAME                          TYPE                                  DATA   AGE
dashboard-admin-token-7r27j   kubernetes.io/service-account-token   3      18d
```
5. Print the token
```
kubectl describe secret dashboard-admin-token-7r27j
```
Now the dashboard is available on `localhost:8001` we can expose localhost by  running `kubectl proxy`.

6. Enter the username dashboard-admin and token into the login page
```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login
```

# Using kubectl locally
You can set up kubectl on your local machine so that you don't have to ssh everytime. 
1. Download the kubectl [binary](https://kubernetes.io/docs/tasks/tools/install-kubectl) 
```
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.18.0/bin/linux/amd64/kubectl
```
2. Copy the kube config files
```
scp -r user@mymasternode:~/.kube .kube
```
Now when you invoke `./kubectl` on your local machine it will connect to your cluster