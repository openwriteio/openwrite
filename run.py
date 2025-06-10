from openwrite import create_app
app = create_app()

if __name__ == "__main__":
    import os
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=os.environ.get("IP", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=True)
