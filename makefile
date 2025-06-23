include .env
export

deploy:
	adk deploy cloud_run \
		--project $(GOOGLE_CLOUD_PROJECT) \
		--region $(GOOGLE_CLOUD_LOCATION) \
		--service_name $(AGENT_SERVICE_NAME) \
		--with_ui \
		src/agents/EchoQL_Agent

delete:
	gcloud run services delete $(AGENT_SERVICE_NAME) \
		--region $(GOOGLE_CLOUD_LOCATION) \
		--project $(GOOGLE_CLOUD_PROJECT) --quiet

list:
	gcloud run services list \
		--region $(GOOGLE_CLOUD_LOCATION) \
		--project $(GOOGLE_CLOUD_PROJECT)

logs:
	gcloud logging read \
		"logName=projects/$(GOOGLE_CLOUD_PROJECT)/logs/run.googleapis.com%2Fstdout AND resource.labels.service_name=$(AGENT_SERVICE_NAME)" \
		--limit=50 \
		--project=$(GOOGLE_CLOUD_PROJECT) \
		--format="table(timestamp, textPayload)"

url:
	gcloud run services describe $(AGENT_SERVICE_NAME) \
		--region $(GOOGLE_CLOUD_LOCATION) \
		--project $(GOOGLE_CLOUD_PROJECT) \
		--format="value(status.url)"
