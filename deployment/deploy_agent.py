import os
from vertexai.preview import agent_engines
from src.agents.EchoQL_Agent.agent import root_agent

# Set environment variables (from .env)
env_vars = {
    "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
    "GOOGLE_CLOUD_PROJECT": "adk-hackathon-461216",
    "GOOGLE_CLOUD_LOCATION": "europe-west3",
    "GOOGLE_CLOUD_STAGING_BUCKET": "gs://data-collection-agent",
    "VERTEX_INDEX_ENDPOINT_ID": "projects/adk-hackathon-461216/locations/europe-west3/indexEndpoints/5165259336687026176",
    "VERTEX_DEPLOYED_INDEX_ID": "table-schema-endpoint",
    "EMBEDDING_MODEL": "textembedding-gecko@003",
    "EMBEDDING_DIM": "768",
    "FAST_LLM_MODEL": "gemini-1.5-flash",
    "REASONING_MODEL": "gemini-1.5-pro",
}

# Requirements for deployment
requirements = [
    "google-cloud-aiplatform[agent_engines,adk]",
    # Add any other requirements from requirements.txt if needed
]

# Optional: extra_packages if you have a wheel to upload
extra_packages = []

display_name = "Data Analysis Agent"
description = "Checks data availability, generates SQL, validates it, executes the query, and returns a CSV to the user."

def main():
    print("Deploying agent to Vertex AI Agent Engine...")
    remote_agent = agent_engines.create(
        root_agent,
        requirements=requirements,
        extra_packages=extra_packages,
        display_name=display_name,
        description=description,
        env_vars=env_vars,
    )
    print("Deployed agent resource name:", remote_agent.resource_name)
    print("Deployment complete! Use the resource name to construct your endpoint URL.")

if __name__ == "__main__":
    main() 