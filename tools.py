from langchain.agents import Tool
import requests

def api_call(action, data=None):
    url = "http://127.0.0.1:8000/api/products/"
    headers = {"Content-Type": "application/json"}

    print(data)

    if action == "create":
        response = requests.post(url, json=data, headers=headers)
    elif action == "retrieve":
        response = requests.get(f"{url}{data}/", headers=headers)
    elif action == "update":
        response = requests.put(f"{url}{data['id']}/", json=data, headers=headers)
    elif action == "delete":
        response = requests.delete(f"{url}{data}/", headers=headers)
    else:
        return "Invalid action"

    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    elif response.status_code == 204:
        return "Successfully deleted"
    else:
        return f"Error: {response.status_code} - {response.text}"


class APITool:
    def __init__(self, action):
        self.action = action

    def __call__(self, tool_input):
        if isinstance(tool_input, str):
            try:
                import json
                data = json.loads(tool_input)
            except json.JSONDecodeError:
                data = {"id": tool_input}
        else:
            data = tool_input

        return api_call(self.action, data)

create_tool = Tool(
    name="CreateProduct",
    func=APITool("create"),
    description='Creates a new product. Provide "name", "description", and "price" fields only.'
)

retrieve_tool = Tool(
    name="RetrieveProduct",
    func=APITool("retrieve"),
    description='Retrieves a product by its "id".'
)

update_tool = Tool(
    name="UpdateProduct",
    func=APITool("update"),
    description='Updates a product by its "name" and provided "description", or "price"'
)

delete_tool = Tool(
    name="DeleteProduct",
    func=APITool("delete"),
    description='Deletes a product by its "name".'
)