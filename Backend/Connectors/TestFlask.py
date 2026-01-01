from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import threading
from Backend.Connectors.MCP.TestClient import MCPClient

class AsyncLoopRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self._start_loop,
            daemon=True,
        )
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop).result()

app = Flask(__name__)
CORS(app)

loop_runner = AsyncLoopRunner()
mcp_client = MCPClient()

loop = loop_runner.run(mcp_client.setup())

@app.route('/api/data', methods=['POST'])
async def receive_data():
    data = request.json
    query = data.get('query', '')

    answer = loop_runner.run(mcp_client.generate_answer(query=str(query)))

    return jsonify({'message': answer,})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
