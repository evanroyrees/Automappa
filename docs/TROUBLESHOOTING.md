# Troubleshooting

## Celery, RabbitMQ task-queue

### Resources

- [celery rabbitmq tutorial](https://suzannewang.com/celery-rabbitmq-tutorial/)

## docker-compose services configuration

***NOTE: All of this assumes you have all docker services running via `make up` or `docker-compose up`***

> ~Provision grafana from `docker-compose.yml`. See: [Grafana provisioning example data source config file](https://grafana.com/docs/grafana/latest/administration/provisioning/#example-data-source-config-file)~
> Found a nice blog post and accompanying GitHub repo to follow:
>
> - [Medium blog post](https://medium.com/swlh/easy-grafana-and-docker-compose-setup-d0f6f9fcec13)
> - [github.com/annea-ai/grafana-infrastructure](<https://github.com/annea-ai/grafana-infrastructure>)
> - [Grafana docs on Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)

### Monitoring Services

- RabbitMQ management - [http://localhost:15672](http://localhost:15672)
- Flower link - [http://localhost:5555](http://localhost:5555)
- Prometheus link - [http://localhost:9090](http://localhost:9090)
- Grafana link - [http://localhost:3000](http://localhost:3000)

### Grafana configuration

- flower+prometheus+grafana [add prometheus as a data source in grafana](<https://flower.readthedocs.io/en/latest/prometheus-integration.html#add-prometheus-as-a-data-source-in-grafana> "flower+prometheus+grafana add prometheus as a data source in grafana")
- grafana link - [http://localhost:3000](http://localhost:3000)

Add the prometheus url as:

```bash
http://prometheus:9090
```

Notice the tutorial mentions `http://localhost:9090`, but since this is running as a service using `docker-compose` the hostname changes to the
`prometheus` alias (this is the name of the service in the `docker-compose.yml` file)
