#!/usr/bin/env python3
import connexion

app = connexion.App(__name__, debug=True)
app.add_api('api.yaml')
app.run(host="0.0.0.0", port=5247)
