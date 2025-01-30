from some_app import app


#Using uWSGI
#def web_app(enviroment, response):
#    status = '200 OK'
#    headers = [('Content-type', 'text/html; charset=utf-8')]
#    response(status, headers)
#    return app.run()



if __name__ == "__main__":
    app.run()
#    web_app()