# Spark for Kubernetes
We will run Spark standalone in containers. Ensure that [GlusterFs](https://github.com/pgigeruzh/spark#glusterfs) is installed.

1. Create a GlusterFS service. 
```
kubectl apply -f glusterfs.yaml
```
`glusterfs.yaml`
```
apiVersion: v1
kind: Service
metadata:
  name: glusterfs-cluster
spec:
  ports:
  - port: 24000
---
apiVersion: v1
kind: Endpoints
metadata:
  name: glusterfs-cluster
subsets:
- addresses:
  - ip: 192.168.0.100
  ports:
  - port: 24000
- addresses:
  - ip: 192.168.0.101
  ports:
  - port: 24000
- addresses:
  - ip: 192.168.0.102
  ports:
  - port: 24000
- addresses:
  - ip: 192.168.0.103
  ports:
  - port: 24000
```
This will allow communication through port `24000` to the specified ips 

2. Create the Spark Master
```
kubectl apply -f master.yaml
```
`master.yaml`
```
apiVersion: v1
kind: Service
metadata:
  name: spark-master
spec:
  selector:
    app: spark-master
  ports:
  - name: web-ui
    protocol: TCP
    port: 8080
    targetPort: 8080
  - name: master
    protocol: TCP
    port: 7077
    targetPort: 7077
  - name: master-blockmanager
    protocol: TCP
    port: 41001
    targetPort: 41001
  - name: master-driver
    protocol: TCP
    port: 41002
    targetPort: 41002
  externalIPs:
    - 192.168.0.XXX
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-master
  labels:
    app: spark-master
spec:
  selector:
    matchLabels:
      app: spark-master
  template:
    metadata:
      labels:
        app: spark-master
    spec:
      hostname: spark-master
      containers:
      - name: spark-master
        image: pgigeruzh/spark:arm
        command: ["/bin/sh","-c"]
        args: ['unset SPARK_MASTER_PORT; echo "$(hostname -i) spark-master" >> /etc/hosts; bin/spark-class org.apache.spark.deploy.master.Master --ip spark-master --port 7077 --cores 4']
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        - containerPort: 7077
        - containerPort: 41001
        - containerPort: 41002
        volumeMounts:
          - mountPath: /mnt/glusterfs
            name: glusterfsvol
        resources:
          requests:
            cpu: 100m
      volumes:
        - name: glusterfsvol
          glusterfs:
            endpoints: glusterfs-cluster
            path: gfs
            readOnly: false
```
`pgigeruzh/spark:arm` is a spark image we [created](https://github.com/pgigeruzh/spark/blob/master/Dockerfile)  
Ensure `externalIPs` is set to the master node ip so that you can view the SparkUI in you browser.   
Spark uses some random ports for certain services, ensure that these [ports](https://spark.apache.org/docs/latest/configuration.html) are set manually when running spark-submit and are open.

2. Create the Spark Worker
```
kubectl apply -f worker.yaml
```
`worker.yaml`
```
apiVersion: apps/v1
kind: Deployment
#kind: DaemonSet
metadata:
  name: spark-worker
  labels:
    app: spark-worker
spec:
  replicas: 4
  selector:
    matchLabels:
      name: spark-worker
  template:
    metadata:
      labels:
        name: spark-worker
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: spark-worker
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: spark-worker
        image: pgigeruzh/spark:arm
        command: ["/bin/sh","-c"]
        args: ['unset SPARK_MASTER_PORT; bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077 --cores 4']
        imagePullPolicy: Always
        ports:
        - containerPort: 8081
        volumeMounts:
          - mountPath: /mnt/glusterfs
            name: glusterfsvol
        resources:
          requests:
            cpu: 100m
      volumes:
        - name: glusterfsvol
          glusterfs:
            endpoints: glusterfs-cluster
            path: gfs
            readOnly: false
```
You can change the kind to `DaemonSet` (and remove the `Replicas` tag) to ensure the each node runs exactly 1 pod. The assignment of nodes to pods can be set using [anti-affinity](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity).  

3. Check the status of the pods
```
kubectl get pods -o wide

NAME                           READY   STATUS    RESTARTS   AGE   IP          NODE           
nginx                          1/1     Running   0          11d   10.42.0.2   raspberrypi4   
spark-master-dd66f8f77-pfzj6   1/1     Running   0          12d   10.32.0.4   raspberrypi2   
spark-worker-f84d4c4c6-t92mf   1/1     Running   0          12d   10.36.0.3   raspberrypi3   
```
4. Access the container
```
kubectl exec spark-master-dd66f8f77-pfzj6 -it -- bash 
```
5. Run spark-submit
```
spark-submit --master spark://spark-master:7077 --conf spark.driver.port=41002 --conf spark.blockManager.port=41001 /mnt/glusterfs/myfile.py
```

# Copying a file into GlusterFS
1. Mount the virtual volume
```
sudo mount -t glusterfs 192.168.0.100:/gfs /mnt
```
2. Copy you files to the volume
```
sudo cp myfile.py /mnt/
```
Now the file should be visable inside the container under the specified mount path in the yaml file.

# Running pods on the Master Node
To run pods on the master node there are two options:  
i. Specify the [NodeName](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodename) tag in the yaml file, this forces the pod to run on the specified node.  
ii. Untaint the master node:  
```
kubectl taint nodes $(hostname) node-role.kubernetes.io/master:NoSchedule-
```
To retaint rerun the command without the minus sign.