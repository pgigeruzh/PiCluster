# Spark Cluster on Docker Swarm

To deploy spark on docker swarm, you first need to have a "Spark" docker image. The few options available are for x86 and not arm, therefore, you need to either 1) create your own or 2) build/compile an existing one yourself. I have decided to go with the first option. It needs to be noted that, at the time of writing this article, Raspian is still 32 bit and can therefore not run arm64 images. The documentation is in a separate GitHub repo: https://github.com/pgigeruzh/spark
