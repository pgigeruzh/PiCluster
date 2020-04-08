# Installing Kubernetes
The official guide for install Kubernetes can be found [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/). However we will be following the guide from [k8s-on-raspbian](https://github.com/teamserverless/k8s-on-raspbian/blob/master/GUIDE.md). Note that there is exists a light weight version on kubernetes called [K3s](https://blog.alexellis.io/raspberry-pi-homelab-with-k3sup/) and an alternative to Raspbian called [HypriotOS](https://blog.hypriot.com/post/setup-kubernetes-raspberry-pi-cluster/) which is optmized for Docker.

# Common Errors
**Error:** Node not connecting  
**Reason:** Swap partition may comeback after reboot  
**Solution:** `sudo systemctl disable dphys-swapfile.service`

**Error 1:** Error loading config file "/etc/kubernetes/admin.conf"  
**Error 2:** The connection to the server localhost:8080 was refused  
**Reason:**  The sussested code output of `kubeadm init` was not runned  
**Solution:** 
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

**Error:** Unable to connect to the server: x509  
**Reason:** The cluster was restarted without enabling the kublet service  
**Solution:** 
```bash
systemctl daemon-reload
sudo systemctl enable kubelet
```


**Error:**  Cannot get Node "X": nodes "X" is forbidden: User "system:bootstrap:iop179" Cannot get resource "nodes" in API group "" at the cluster scope  
**Reason:** You may have conflicting versions or have updated kubernetes  
**Solution:**   
```bash
# Step 1: Check that the output is the same for all nodes  
dpkg -l | grep -i kube
# Step 2: [Master] Generate new bootstarp token  
sudo kubeadm init phase bootstrap-token 
# Step 3: [Slave]  
sudo rm /etc/kubernetes/pki/ca.crt
sudo kubeadm join <token>`
```
**Error:** Pod network weave-net give error CrashLoopBackOff  
**Reason:**  Did not bridge traffic on all nodes [See [issue](https://gist.github.com/alexellis/fdbc90de7691a1b9edb545c17da2d975#gistcomment-2564487)]  
**Solution:** Try [this](https://github.com/weaveworks/weave/issues/3717#issuecomment-575805360).
Did you run `sudo sysctl net.bridge.bridge-nf-call-iptables=1` on all nodes?

**Error:** The connection to the server X:6443 was refused - did you specify the right host or port?  
**Reason:** You are probaly running `kubectl` on a Slave  
**Solution:** Run on the master node  

# Debugging
`CrashLoopBackOff` on a pod is a very common error. First you should know that images compiled on x86 archetecture will not run on arm32.  
1. Show all pods running:
`kubectl get pods --all-namespaces -o wide`  
2. Show information about the pod: `kubectl describe pod pod-name-xyz1`  
3. Check the logs: `kubectl logs podname-xyz1`  

The logs should tell you more about the error. If you delete a pod it will restart. To stop it from respawning delete the deployment/replication:
```
kubectl get all
kubectl delete deployment.apps/nginx-deployment
```

# Useful Commands
Print join token:  
`kubeadm token create --print-join-command`

Go into the container:  
`kubectl exec podname-<ID> -it -- bash`
