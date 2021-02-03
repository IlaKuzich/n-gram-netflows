# n-gram-netflows


**Hypothesis**

Let's assume that all normal network behavior follow the N number of patterns. This patterns could be observed in dataset and captured by model. Then everything is not match captured patterns will be marked as anomaly. To measure how precise sequence matches patterns we will calculate entropy and perplexity.

**Dataset**

To build and evaluate model I've used. CTU-13 https://www.stratosphereips.org/datasets-ctu13

**Experiment**

To check the hypothesis the following the experiment was performed.
Language model:
Ngrams with Laplacian smoothing. N=4

Training dataset: CTU-13(1, 2, 3, 4, 5, 6) botnet flows was filtered out.
 
Before using netflows was encoded to token. Encoding procedure is following.

* Protocol (tcp, udp)
* Flags tcp - FSPRAU
* Protocol. (From list of protocol or "Unknown" if not found)
* Log10 payload size.

Examples: udp_CON_Domain Name Server_2.0, tcp_SRPA_HTTP protocol over TLS/SSL_3.0

You can see, that in average bot netflows has higher perplexity. It means that botnet flows has different patterns than normal. 

**Run sensor**

To create network and start rabbitmq
```bash
make init
```

In rabbitmq 
1. Create user and define it in ./docker-compose.yml file.
2. Create queues (netflow, anomaly_report) and exchanges 
3. Create exchanges (sensor_out, synthetic_test)

Start sensor
```bash
make start
```
Run experiment
```bash
python ./run_experiment.py
```

To train and evaluate yout own model use ./train_and_evaluate.py
