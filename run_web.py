from cnm.main import app

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(host="0.0.0.0", port="8080")